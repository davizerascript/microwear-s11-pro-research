#!/usr/bin/env python3
"""Preserve unassigned UFW byte ranges without modifying the source.

Requires an explicit new/empty output directory. Existing output is never
removed or overwritten. Header and table CRCs and all payload extents are
validated before any output is written.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
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


def safe_name(name: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return result if result and result not in {".", ".."} else "unnamed"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", required=True, type=Path, help="new or empty output directory")
    args = ap.parse_args()
    source = args.input
    raw = source.read_bytes()
    if raw[:2] == b"\xbc\xaf":
        raise ValueError("Qix-wrapped UFW is not supported by this script")
    if len(raw) < 0x40:
        raise ValueError("input is shorter than the UFW header")
    outer = mod.dec(raw[:0x40])
    stored_header_crc, stored_list_crc, imgsize, count, _wa3, _wa4 = __import__("struct").unpack_from("<HHIHHI", outer, 0)
    if imgsize != len(raw) or count > 64:
        raise ValueError(f"invalid UFW size/count: declared={imgsize}, actual={len(raw)}, entries={count}")
    table_end = 0x40 + count * 0x50
    if table_end > len(raw):
        raise ValueError("entry table extends beyond input")
    calc_header_crc = jl_crc16(outer[2:0x40])
    calc_list_crc = jl_crc16(raw[0x40:table_end])
    if calc_header_crc != stored_header_crc or calc_list_crc != stored_list_crc:
        raise ValueError(
            f"UFW CRC mismatch: header {stored_header_crc:04x}/{calc_header_crc:04x}, "
            f"list {stored_list_crc:04x}/{calc_list_crc:04x}"
        )

    entries = []
    intervals = []
    for i in range(count):
        offset = 0x40 + i * 0x50
        decoded = mod.dec(raw[offset:offset + 0x50])
        import struct
        etype, idx, dcrc, _reserved, data_off, size, _u1, _extra, namebytes = struct.unpack_from(
            "<HHHHIII44s16s", decoded, 0
        )
        name = namebytes.split(b"\x00", 1)[0].decode("ascii", "replace")
        if size and data_off < table_end:
            raise ValueError(f"entry {i} {name!r} overlaps the UFW table")
        if data_off > len(raw) or size > len(raw) - data_off:
            raise ValueError(f"entry {i} {name!r} exceeds input bounds")
        if size:
            intervals.append((data_off, data_off + size, i, name))
        entries.append({"slot": i, "type": etype, "index": idx, "name": name,
                        "entry_offset": offset, "data_offset": data_off, "size": size,
                        "data_crc16_stored": dcrc})
    intervals.sort()
    for prev, cur in zip(intervals, intervals[1:]):
        if cur[0] < prev[1]:
            raise ValueError(f"overlapping UFW payload ranges: {prev[3]!r} and {cur[3]!r}")

    requested_out = args.out.expanduser()
    if requested_out.is_symlink():
        raise ValueError("refusing a symlink output directory")
    out = requested_out.resolve()
    if out.exists() and not out.is_dir():
        raise ValueError("output path exists and is not a directory")
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError(f"output directory must be empty: {out}")
    gaps_dir = out / "gaps"
    metadata_dir = out / "metadata"
    gaps_dir.mkdir()
    metadata_dir.mkdir()

    manifest = []
    def save(path: Path, data: bytes, offset: int, kind: str):
        if path.is_symlink() or not path.resolve().is_relative_to(out):
            raise ValueError(f"unsafe output path: {path}")
        with path.open("xb") as stream:
            stream.write(data)
        manifest.append({"file": str(path.relative_to(out)), "kind": kind,
                         "offset": offset, "offset_hex": f"0x{offset:x}",
                         "end_exclusive": offset + len(data),
                         "end_exclusive_hex": f"0x{offset + len(data):x}",
                         "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})

    save(metadata_dir / "outer_header_table.raw.bin", raw[:table_end], 0,
         "raw UFW header and entry table")
    save(metadata_dir / "outer_header.decoded.bin", bytes(outer), 0,
         "UFW header decoded in memory")
    for item in entries:
        i, offset = item["slot"], item["entry_offset"]
        save(metadata_dir / f"entry_{i:02d}.raw.bin", raw[offset:offset + 0x50], offset,
             "raw UFW entry record")
        save(metadata_dir / f"entry_{i:02d}.decoded.bin", bytes(mod.dec(raw[offset:offset + 0x50])), offset,
             "UFW entry record decoded in memory")

    for start, end, i, name in intervals:
        if start < table_end:
            raise ValueError("payload range begins before the end of metadata")
        if start > table_end:
            gapname = f"gap_{table_end:08x}_{start:08x}.bin"
            save(gaps_dir / gapname, raw[table_end:start], table_end,
                 "unassigned bytes between UFW metadata/payloads")
        table_end = end
    if table_end < len(raw):
        gapname = f"gap_{table_end:08x}_{len(raw):08x}.bin"
        save(gaps_dir / gapname, raw[table_end:], table_end,
             "trailing unassigned bytes")

    report = {"source": str(source), "source_sha256": hashlib.sha256(raw).hexdigest(),
              "table_end": 0x40 + count * 0x50, "entry_count": count,
              "header_crc16_stored": stored_header_crc, "header_crc16_calculated": calc_header_crc,
              "list_crc16_stored": stored_list_crc, "list_crc16_calculated": calc_list_crc,
              "entries": entries, "regions": manifest}
    with (out / "manifest.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"out": str(out), "table_end": hex(report["table_end"]),
                      "regions": len(manifest), "source_sha256": report["source_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
