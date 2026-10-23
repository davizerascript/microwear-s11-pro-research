#!/usr/bin/env python3
"""Read-only JieLi UFW inspector/extractor for the sample format.

The source is never opened for writing. Extraction requires a new/empty output
folder. UFW header/list CRCs and the raw flash.bin CRC are checked. CRC fields
for other entries are reported over raw bytes but are not treated as failures
when their scope is unknown.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

PARSER = Path(__file__).resolve().parents[1] / "work/jieli-research/tools/ufw-repack/parse_outer.py"
sys.path.insert(0, str(PARSER.parent))
spec = importlib.util.spec_from_file_location("parse_outer", PARSER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load public UFW parser: {PARSER}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from jltech.crc import jl_crc16


def safe_component_name(name: str) -> str:
    """Map an untrusted UFW name to a single conservative filename component."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return cleaned if cleaned and cleaned not in {".", ".."} else "unnamed"


def parse(path: Path):
    raw = path.read_bytes()
    if raw[:2] == b"\xbc\xaf":
        raise ValueError("Qix-wrapped UFW is outside this extractor's supported format")
    if len(raw) < 0x40:
        raise ValueError("input is shorter than the 0x40-byte UFW header")
    hdr = mod.dec(raw[:0x40])
    hdrcrc, listcrc, imgsize, count, _wa3, _wa4 = struct.unpack_from("<HHIHHI", hdr, 0)
    chip = hdr[0x10:0x40].split(b"\0")[0].decode("ascii", "replace")
    if imgsize != len(raw) or count > 64:
        raise ValueError(f"Implausible UFW header: declared_size={imgsize}, entries={count}, actual={len(raw)}")
    table_end = 0x40 + count * 0x50
    if table_end > len(raw):
        raise ValueError("UFW entry table extends beyond file")
    calculated_header_crc = jl_crc16(hdr[2:0x40])
    calculated_list_crc = jl_crc16(raw[0x40:table_end])
    if hdrcrc != calculated_header_crc:
        raise ValueError(f"UFW header CRC mismatch: stored=0x{hdrcrc:04x} calculated=0x{calculated_header_crc:04x}")
    if listcrc != calculated_list_crc:
        raise ValueError(f"UFW entry-list CRC mismatch: stored=0x{listcrc:04x} calculated=0x{calculated_list_crc:04x}")

    entries = []
    intervals = []
    for i in range(count):
        off = 0x40 + i * 0x50
        e = mod.dec(raw[off:off + 0x50])
        etype, idx, dcrc, _reserved, data_off, size, _u1, _u2, namebytes = struct.unpack_from(
            "<HHHHIII44s16s", e
        )
        name = namebytes.split(b"\0")[0].decode("ascii", "replace")
        if size and data_off < table_end:
            raise ValueError(f"Entry {i} {name!r} overlaps the UFW header/table")
        if data_off > len(raw) or size > len(raw) - data_off:
            raise ValueError(f"Entry {i} {name!r} exceeds file bounds")
        payload = raw[data_off:data_off + size]
        raw_crc = jl_crc16(payload)
        if etype == 0 and dcrc != raw_crc:
            raise ValueError(f"flash.bin raw CRC mismatch: stored=0x{dcrc:04x} calculated=0x{raw_crc:04x}")
        if size:
            intervals.append((data_off, data_off + size, i, name))
        entries.append({
            "slot": i, "type": etype, "index": idx,
            "data_crc16_stored": dcrc,
            "data_crc16_calculated_raw": raw_crc,
            "data_crc16_matches_raw": dcrc == raw_crc,
            "data_crc_scope_status": "raw_match" if dcrc == raw_crc else "raw_mismatch_scope_unresolved",
            "offset": data_off, "size": size, "name": name,
        })
    intervals.sort()
    for previous, current in zip(intervals, intervals[1:]):
        if current[0] < previous[1]:
            raise ValueError(f"UFW payload ranges overlap: {previous[3]!r} and {current[3]!r}")

    header = {
        "header_crc16": hdrcrc,
        "header_crc16_calculated": calculated_header_crc,
        "header_crc_ok": True,
        "list_crc16": listcrc,
        "list_crc16_calculated": calculated_list_crc,
        "list_crc_ok": True,
        "declared_size": imgsize,
        "entry_count": count,
        "table_end": table_end,
        "chip": chip,
    }
    return raw, header, entries


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, help="Extract entries into a new or empty directory")
    args = ap.parse_args()
    raw, header, entries = parse(args.input)
    report = {
        "input": str(args.input),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "crc16_parameters": {
            "polynomial": "0x1021", "initial": "0x0000", "refin": False,
            "refout": False, "xorout": "0x0000", "stored_field_endian": "little-endian",
        },
        **header,
        "entries": entries,
    }
    if args.out:
        requested_out = args.out.expanduser()
        if requested_out.is_symlink():
            raise ValueError("refusing a symlink output directory")
        out = requested_out.resolve()
        if out.exists() and not out.is_dir():
            raise ValueError("output path exists and is not a directory")
        out.mkdir(parents=True, exist_ok=True)
        if any(out.iterdir()):
            raise ValueError(f"output directory must be empty: {out}")
        for e in entries:
            payload = raw[e["offset"]:e["offset"] + e["size"]]
            filename = f'{e["slot"]:02d}_{safe_component_name(e["name"])}.bin'
            dest = out / filename
            if dest.is_symlink() or not dest.resolve().is_relative_to(out):
                raise ValueError(f"unsafe output path: {dest}")
            with dest.open("xb") as stream:
                stream.write(payload)
            e["extracted_file"] = filename
            e["sha256"] = hashlib.sha256(payload).hexdigest()
        inv = out / "inventory.json"
        with inv.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
