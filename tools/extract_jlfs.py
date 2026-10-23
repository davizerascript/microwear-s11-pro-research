#!/usr/bin/env python3
"""Decode and extract the JLFS tree from this UFW using public JieLi routines.

A synthetic Qix prefix is supplied in memory only to reuse a parser whose
front-end requires Qix. The source UFW is never modified.
This sample-bound script refuses a nonempty output directory; move prior
derived output aside before a deliberate rerun. It requires the local public
parser checkout at work/jieli-research and an extracted flash.bin.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "work/jieli-research"
PARSER = REPO / "tools/ufw-repack/repack_ufw.py"
OUT = ROOT / "work/decoded/jlfs"
RAW_FLASH = ROOT / "work/extracted/00_flash.bin.bin"
sys.path.insert(0, str(REPO / "tools/ufw-repack"))
spec = importlib.util.spec_from_file_location("jieli_repack_parser", PARSER)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
from jltech.crc import jl_crc16
from jltech.cipher import jl_enc_cipher

src = ROOT / "original/176103986767848.ufw"
raw = src.read_bytes()
# The temporary prefix is not written; parse_ufw reads the genuine UFW at byte 27.
layout = mod.parse_ufw(b"\xbc\xaf" + b"\x00" * 25 + raw)
flash = layout.flash_bin_plain
if OUT.exists() and any(OUT.iterdir()):
    raise SystemExit(f"refusing to overwrite nonempty output directory: {OUT}")
OUT.mkdir(parents=True, exist_ok=True)


def safe(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return value or "unnamed"


def descramble_bankcb(data: bytes, key: int = 0xFFFF) -> tuple[bytes, dict]:
    """Apply the public SPL bankcb transform and validate both embedded CRCs."""
    if len(data) < 16:
        raise ValueError("uboot.boot is shorter than its 16-byte bankcb header")
    decoded = bytearray(data)
    jl_enc_cipher(decoded, 0, 16, key)
    bank_header = bytes(decoded[:14])
    stored_header_crc = int.from_bytes(decoded[14:16], "little")
    calculated_header_crc = jl_crc16(bank_header)
    if stored_header_crc != calculated_header_crc:
        raise ValueError("bankcb header CRC mismatch; refusing to transform SPL payload")
    bank_id, bank_size, bank_load, bank_offset, bank_crc = struct.unpack("<HHIIH", bank_header)
    if bank_offset > len(decoded) or bank_size > len(decoded) - bank_offset:
        raise ValueError("bankcb payload range exceeds uboot.boot bounds")
    jl_enc_cipher(decoded, bank_offset, bank_size, key)
    body_crc = jl_crc16(decoded[bank_offset:bank_offset + bank_size])
    if body_crc != bank_crc:
        raise ValueError("bankcb body CRC mismatch after descramble")
    return bytes(decoded), {
        "bank_id": bank_id,
        "bank_size": bank_size,
        "bank_load": bank_load,
        "bank_offset": bank_offset,
        "bank_header_crc16": stored_header_crc,
        "bank_header_crc16_calculated": calculated_header_crc,
        "bank_crc16": bank_crc,
        "bank_crc16_calculated": body_crc,
        "payload_crc16_after_bankcb": jl_crc16(decoded),
        "decompression_performed": False,
    }


def save_payload(record: dict, data: bytes, kind: str) -> None:
    component_name = safe(record["name"])
    suffix = Path(component_name).suffix
    filename = f'{record["header_offset"]:08x}_{component_name}'
    if not suffix:
        filename += ".bin"
    rel = Path("work/decoded/jlfs") / filename
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    record["extracted_file"] = str(rel)
    record["sha256"] = hashlib.sha256(data).hexdigest()
    record["actual_size"] = len(data)
    record["data_crc16_calculated_on_saved_bytes"] = jl_crc16(data) if data else 0
    record["data_crc_matches_saved_bytes"] = (
        record["data_crc16"] == 0xFFFF
        or record["data_crc16"] == record["data_crc16_calculated_on_saved_bytes"]
    )
    record["data_crc_saved_bytes_note"] = (
        "Calculated over exactly the bytes written to this file; encrypted/compressed entries may require a format-specific transform."
    )
    record["kind"] = kind


def entry_record(offset: int, data: bytes, parent_base: int, index: int) -> dict:
    if len(data) != 32:
        raise ValueError("short JLFS entry header")
    hcrc, dcrc, rel, size, flags, reserved, entry_index, name_bytes = struct.unpack("<HHIIBBH16s", data)
    name = name_bytes.split(b"\0")[0].decode("ascii", "replace")
    return {
        "header_offset": offset,
        "header_offset_hex": hex(offset),
        "header_crc16": hcrc,
        "header_crc16_calculated": jl_crc16(data[2:]),
        "header_crc_ok": hcrc == jl_crc16(data[2:]),
        "data_crc16": dcrc,
        "relative_offset": rel,
        "relative_offset_hex": hex(rel),
        "size_field": size,
        "size_bytes": size,
        "flags": flags,
        "reserved": reserved,
        "index": entry_index,
        "name": name,
        "parent_base": parent_base,
        "data_offset": parent_base + rel,
        "data_offset_hex": hex(parent_base + rel),
        "table_index": index,
    }


def parse_nested(parent: dict, depth: int = 1) -> list[dict]:
    if depth > 4:
        raise ValueError("directory nesting exceeded safety limit")
    result = []
    start = parent["data_offset"]
    end = start + parent.get("data_size", parent["size_field"])
    if start < 0 or end > len(flash):
        parent["contents_available"] = False
        return result
    cursor = start
    maximum = min((end - start) // 32, 4096)
    for idx in range(maximum):
        record = entry_record(cursor, flash[cursor:cursor + 32], parent["header_offset"], idx)
        record["within_flash_dump"] = record["data_offset"] >= 0 and record["data_offset"] + record["size_field"] <= len(flash)
        if not record["header_crc_ok"]:
            record["parse_note"] = "Header CRC mismatch; record not accepted as a valid child."
            result.append(record)
            break
        if (record["flags"] & 0x03) == 0x03:
            record["directory"] = True
            record["data_size"] = record["size_field"]
            if record["within_flash_dump"]:
                payload = flash[record["data_offset"]:record["data_offset"] + record["size_field"]]
                save_payload(record, payload, "nested JLFS directory body")
                record["children"] = parse_nested(record, depth + 1)
        elif record["within_flash_dump"] and record["data_crc16"] != 0xFFFF:
            payload = flash[record["data_offset"]:record["data_offset"] + record["size_field"]]
            save_payload(record, payload, "nested JLFS file")
        else:
            record["content_status"] = "Partition reference or payload outside this update image; no data extracted."
        result.append(record)
        if record["index"] != 0:
            break
        cursor += 32
    return result


# JLFS flash header: validate the fully decrypted bytes before restoring visible VID/PID.
raw_header = RAW_FLASH.read_bytes()[:32]
header_crc_input = bytearray(raw_header)
jl_enc_cipher(header_crc_input, 0, 32, 0xFFFF)
header_crc_stored = int.from_bytes(header_crc_input[:2], "little")
header_crc_calculated = jl_crc16(header_crc_input[2:])
header_display = bytearray(header_crc_input)
header_display[4:8] = raw_header[4:8]
header_display[16:32] = raw_header[16:32]
(OUT / "flash_header_crc_input.bin").write_bytes(header_crc_input)
(OUT / "flash_header_decoded_candidate.bin").write_bytes(header_display)
flash_header = {
    "offset": 0,
    "size": 32,
    "raw_hex": raw_header.hex(),
    "decrypted_crc_input_hex": bytes(header_crc_input).hex(),
    "decoded_candidate_hex": bytes(header_display).hex(),
    "header_crc16": header_crc_stored,
    "header_crc16_calculated": header_crc_calculated,
    "header_crc_ok": header_crc_stored == header_crc_calculated,
    "header_crc_range": "decrypted bytes [0x02,0x20) before restoring visible VID/PID",
    "burner_size": int.from_bytes(header_display[2:4], "little"),
    "vid": header_display[4:8].decode("ascii", "replace"),
    "flash_size_field": int.from_bytes(header_display[8:12], "little"),
    "fs_version": header_display[12],
    "block_align_256B_units": header_display[13],
    "reserved": header_display[14],
    "special_options": header_display[15],
    "product_id": header_display[16:32].split(b"\xff")[0].decode("ascii", "replace"),
}

records = []
# Root entries: bootloader, top-level configuration, app area anchor and key_mac map.
for entry in layout.jlfs_top:
    record = {
        "tree": "JLFS top",
        "name": entry.name,
        "header_offset": entry.hdr_off,
        "header_offset_hex": hex(entry.hdr_off),
        "header_crc16": int.from_bytes(entry.plain_header[:2], "little"),
        "header_crc16_calculated": jl_crc16(entry.plain_header[2:]),
        "header_crc_ok": int.from_bytes(entry.plain_header[:2], "little") == jl_crc16(entry.plain_header[2:]),
        "data_crc16": entry.data_crc,
        "relative_or_absolute_offset": entry.eoff,
        "size_field": entry.esize,
        "flags": entry.eflags,
        "index": entry.eindex,
        "data_offset": entry.eoff,
        "data_offset_hex": hex(entry.eoff),
        "size_bytes": entry.esize,
    }
    end = entry.eoff + entry.esize
    record["within_flash_dump"] = entry.eoff >= 0 and end <= len(flash)
    if entry.name == "isd_config.ini" and record["within_flash_dump"]:
        data = flash[entry.eoff:end]
        save_payload(record, data, "JLFS top configuration with CRC-validated chipkey blob")
        chipkey_blob = data[:32]
        stored_crc = int.from_bytes(data[32:34], "little")
        from jltech.chipkeybin import chipkeybin_decode
        record["chipkey_blob_crc16_stored"] = stored_crc
        record["chipkey_blob_crc16_calculated"] = jl_crc16(chipkey_blob)
        record["chipkey_blob_crc_ok"] = stored_crc == jl_crc16(chipkey_blob)
        record["decoded_chipkey"] = f"0x{chipkeybin_decode(chipkey_blob):04x}" if record["chipkey_blob_crc_ok"] else None
        record["remaining_config_hex"] = data[34:].hex()
    elif entry.name == "uboot.boot" and record["within_flash_dump"]:
        data = flash[entry.eoff:end]
        save_payload(record, data, "Raw JLFS SPL payload before bankcb descramble; bit 0x40 denotes LZ4 per public format docs; not decompressed")
        bankcb_payload, bankcb_info = descramble_bankcb(data)
        derived_name = f'{entry.hdr_off:08x}_{safe(entry.name)}.bankcb.bin'
        derived_rel = Path("work/decoded/jlfs") / derived_name
        derived_path = ROOT / derived_rel
        derived_path.write_bytes(bankcb_payload)
        record["bankcb_descramble"] = bankcb_info
        record["bankcb_descrambled_file"] = str(derived_rel)
        record["bankcb_descrambled_sha256"] = hashlib.sha256(bankcb_payload).hexdigest()
        record["bankcb_descrambled_size"] = len(bankcb_payload)
        record["data_crc16_after_bankcb_descramble"] = bankcb_info["payload_crc16_after_bankcb"]
        record["data_crc_matches_after_bankcb_descramble"] = (
            record["data_crc16"] == bankcb_info["payload_crc16_after_bankcb"]
        )
        record["decompression_performed"] = False
    elif entry.eflags == 0x81 and entry.name == "app_dir_head":
        record["content_status"] = "Directory anchor; application region parsed via the SFC-aware iterator."
    elif record["within_flash_dump"] and entry.data_crc != 0xFFFF:
        data = flash[entry.eoff:end]
        save_payload(record, data, "JLFS top-level payload")
    else:
        record["content_status"] = "Absolute/special flash-region reference; data is not present in this update image."
    records.append(record)

# SFC application area and first-level children/directories.
for entry in layout.jlfs_app_dir:
    record = {
        "tree": "app area / SFC root",
        "name": entry.name,
        "header_offset": entry.hdr_off,
        "header_offset_hex": hex(entry.hdr_off),
        "header_crc16": int.from_bytes(entry.plain_header[:2], "little"),
        "header_crc16_calculated": jl_crc16(entry.plain_header[2:]),
        "header_crc_ok": int.from_bytes(entry.plain_header[:2], "little") == jl_crc16(entry.plain_header[2:]),
        "data_crc16": entry.data_crc,
        "relative_or_absolute_offset": entry.eoff,
        "size_field": entry.esize,
        "flags": entry.eflags,
        "index": entry.eindex,
        "data_offset": entry.data_offset,
        "data_offset_hex": hex(entry.data_offset),
        "size_bytes": entry.data_size,
    }
    start, end = entry.data_offset, entry.data_offset + entry.data_size
    record["within_flash_dump"] = start >= 0 and end <= len(flash)
    if entry.name in ("VM", "PRCT", "BTIF", "FATFSI") or not record["within_flash_dump"]:
        record["content_status"] = "Partition/address-map entry; referenced bytes are outside this update image."
    elif entry.name in ("tone", "ui_upgrade", "EXT_RESERVED"):
        body = flash[start:end]
        save_payload(record, body, "JLFS directory body after SFC decryption")
        record["data_size"] = entry.data_size
        record["children"] = parse_nested(record)
    elif entry.name == "app_area_head":
        body = flash[start:end]
        save_payload(record, body, "Application-area region after SFC decryption; overlaps its child payload ranges by design")
    else:
        data = flash[start:end]
        save_payload(record, data, "JLFS data after SFC decryption")
    records.append(record)

report = {
    "source": "original/176103986767848.ufw",
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "chip_from_ufw": "JL701N",
    "container_type": "UFW without Qix wrapper; synthetic prefix used only in memory for compatible parser",
    "crc16_parameters": {
        "polynomial": "0x1021", "initial": "0x0000", "refin": False,
        "refout": False, "xorout": "0x0000", "stored_field_endian": "little-endian",
    },
    "jlfs_flash_header": flash_header,
    "top_level_chipkey": next((r.get("decoded_chipkey") for r in records if r.get("decoded_chipkey")), None),
    "flash_bin_size": len(flash),
    "sfc_decrypted_extent_end": layout.sfc_dec_end,
    "records": records,
}
(OUT / "jlfs-inventory.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
print("flash header", json.dumps(flash_header, indent=2))
print("chipkey", report["top_level_chipkey"], "sfc_end", hex(layout.sfc_dec_end))
for record in records:
    print(record["tree"], record["name"], f'hdr={record["header_offset_hex"]} data={record["data_offset_hex"]} size={record["size_bytes"]:#x}', "hdr_crc", record["header_crc_ok"], "within", record["within_flash_dump"], "data_crc_matches_saved_bytes", record.get("data_crc_matches_saved_bytes"), "file", record.get("extracted_file"))
    for child in record.get("children", []):
        print("  ", child["name"], f'hdr={child["header_offset_hex"]} data={child["data_offset_hex"]} size={child["size_bytes"]:#x}', "hdr_crc", child["header_crc_ok"], "within", child["within_flash_dump"], "data_crc_matches_saved_bytes", child.get("data_crc_matches_saved_bytes"), "file", child.get("extracted_file"))
