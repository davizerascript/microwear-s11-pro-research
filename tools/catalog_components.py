#!/usr/bin/env python3
"""Build a raw-byte inventory from a UFW extraction manifest.

The tool verifies extracted size/hash when present in the manifest and reports
CRC-16 only over raw extracted bytes. It does not infer unknown CRC domains.
Both output paths are explicit and must not already exist.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work/jieli-research/tools/ufw-repack"))
from jltech.crc import jl_crc16

LABELS = {
    "flash.bin": ("Raw payload named flash.bin; internal structure analyzed separately", "High for filename; structural finding is separate"),
    "info.log": ("Empty entry named info.log", "High for observed bytes"),
    "uboot.version": ("Opaque 32-byte entry named uboot.version", "Low for function"),
    "isd_config.ini": ("Opaque outer UFW entry; distinct from the internal 127-byte JLFS file", "Low for function"),
    "v_ota.bin": ("Opaque 64-byte entry named v_ota.bin", "Low for function"),
    "ota.bin": ("Payload named ota.bin; visible strings observed, format not parsed", "Medium for update-related label; low for internal layout"),
    "farg.cfg": ("Opaque 5-byte entry named farg.cfg", "Low for function"),
    "blimit.bin": ("Candidate JLDGAUTH decode documented separately; not validated by this catalog", "Hypothesis"),
    "tail.bin": ("64-byte entry named tail.bin with visible JLUFW marker", "High for observed bytes"),
}


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in Counter(data).values())


def strings(data: bytes, minimum: int = 5, limit: int = 80):
    pattern = rb"[\x20-\x7e]{" + str(minimum).encode() + rb",}"
    return [m.group().decode("ascii", "replace") for m in re.finditer(pattern, data)][:limit]


def analyze(inventory_path: Path, extracted_dir: Path):
    manifest = json.loads(inventory_path.read_text(encoding="utf-8"))
    root = extracted_dir.resolve()
    rows = []
    for e in manifest["entries"]:
        slot = int(e["slot"])
        name = str(e["name"])
        fname = e.get("extracted_file") or f'{slot:02d}_{name}.bin'
        candidate = Path(fname)
        if candidate.is_absolute():
            path = candidate
        else:
            path = extracted_dir / candidate
        if path.is_symlink():
            raise ValueError(f"unsafe extracted-file path in manifest: {fname!r}")
        path = path.resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"unsafe extracted-file path in manifest: {fname!r}")
        b = path.read_bytes()
        size = int(e.get("size", e.get("size_bytes", len(b))))
        if len(b) != size:
            raise ValueError(f"size mismatch for {name!r}: manifest={size}, file={len(b)}")
        sha = hashlib.sha256(b).hexdigest()
        expected_sha = e.get("sha256")
        if expected_sha and expected_sha != sha:
            raise ValueError(f"SHA-256 mismatch for {name!r}")
        declared = int(e.get("data_crc16_stored", e.get("data_crc16", 0)))
        calc = jl_crc16(b)
        label, confidence = LABELS.get(name, ("Unclassified payload", "Unknown"))
        offset = int(e.get("offset", e.get("data_offset", 0)))
        row = {
            "slot": slot, "name": name, "type": e.get("type"), "index": e.get("index"),
            "container_offset": offset, "container_offset_hex": f"0x{offset:x}",
            "size_bytes": len(b), "declared_data_crc16": declared,
            "declared_data_crc16_hex": f"0x{declared:04x}",
            "raw_crc16_calculated": calc, "raw_crc16_calculated_hex": f"0x{calc:04x}",
            "raw_crc_matches_declared": calc == declared,
            "raw_crc_scope_status": "raw_match" if calc == declared else "raw_mismatch_scope_unresolved",
            "sha256": sha, "entropy_bits_per_byte": round(entropy(b), 6),
            "prefix_hex": b[:32].hex(" "), "ascii_strings": strings(b),
            "classification": label, "confidence": confidence,
            "extracted_copy": str(path.relative_to(root)),
        }
        rows.append(row)
    return manifest, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", required=True, type=Path)
    ap.add_argument("--extracted-dir", required=True, type=Path)
    ap.add_argument("--json", required=True, type=Path)
    ap.add_argument("--csv", required=True, type=Path)
    args = ap.parse_args()
    manifest, rows = analyze(args.inventory, args.extracted_dir)
    source = manifest.get("input", manifest.get("source"))
    source_sha = manifest.get("input_sha256", manifest.get("source_sha256"))
    obj = {
        "input": source,
        "input_sha256": source_sha,
        "container_size": manifest.get("declared_size"),
        "outer_header_crc16": manifest.get("header_crc16"),
        "chip_id": manifest.get("chip"),
        "entry_count": len(rows),
        "raw_crc_scope": "CRC-16 over raw extracted entry bytes only; mismatch is not a corruption verdict",
        "entries": rows,
    }
    outputs = [args.json.expanduser(), args.csv.expanduser()]
    if outputs[0] == outputs[1]:
        raise ValueError("JSON and CSV output paths must differ")
    for out in outputs:
        if out.is_symlink() or out.exists():
            raise FileExistsError(f"refusing to overwrite existing output: {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
    with outputs[0].open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    columns = list(rows[0]) if rows else []
    with outputs[1].open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            rendered = row.copy()
            rendered["ascii_strings"] = " | ".join(rendered["ascii_strings"])
            writer.writerow(rendered)
    print(f"Wrote {outputs[0]} and {outputs[1]} ({len(rows)} entries)")
    for row in rows:
        print(f'{row["slot"]:02d} {row["name"]:16s} off={row["container_offset_hex"]:>10s} '
              f'size={row["size_bytes"]:8d} H={row["entropy_bits_per_byte"]:.3f} '
              f'raw_crc_match={row["raw_crc_matches_declared"]} sha256={row["sha256"]}')


if __name__ == "__main__":
    main()
