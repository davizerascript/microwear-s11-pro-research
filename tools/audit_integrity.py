#!/usr/bin/env python3
"""Audit CRC evidence in a JieLi UFW without writing to the input.

Implements the CRC-16 and ENC stream directly so this check does not depend on
CRC libraries or on the extractor's CRC helper. It distinguishes raw stored
bytes from the documented bankcb-descrambled SPL bytes. It does not decompress
uboot.boot or claim that every UFW entry's CRC scope is known.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

POLY = 0x1021
INIT = 0x0000
KEY = 0xFFFF


def crc16(data: bytes, crc: int = INIT) -> int:
    """CRC-16, poly 0x1021, init 0, no reflection, xorout 0."""
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ POLY) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def enc(data: bytes, key: int = KEY) -> bytes:
    """Symmetric JieLi ENC XOR stream; state restarts at each call."""
    out = bytearray(data)
    key &= 0xFFFF
    for i in range(len(out)):
        out[i] ^= key & 0xFF
        key = ((key << 1) ^ (POLY if key & 0x8000 else 0)) & 0xFFFF
    return bytes(out)


def entry_name(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("ascii", "replace")


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    if raw[:2] == b"\xbc\xaf":
        raise ValueError("Qix-wrapped input is not supported by this auditor")
    if len(raw) < 0x40:
        raise ValueError("file is shorter than the UFW header")

    header_plain = enc(raw[:0x40])
    hcrc, listcrc, declared_size, count, _, _ = struct.unpack_from("<HHIHHI", header_plain)
    if count > 64:
        raise ValueError(f"implausible UFW entry count: {count}")
    table_end = 0x40 + count * 0x50
    if table_end > len(raw):
        raise ValueError("UFW entry table exceeds input bounds")

    header_check = crc16(header_plain[2:0x40])
    list_check = crc16(raw[0x40:table_end])
    entries = []
    flash_entry = None
    for i in range(count):
        off = 0x40 + i * 0x50
        e = enc(raw[off:off + 0x50])
        etype, index, stored_crc, _, data_off, size, _, _, ename = struct.unpack_from(
            "<HHHHIII44s16s", e
        )
        name = entry_name(ename)
        if data_off > len(raw) or size > len(raw) - data_off:
            raise ValueError(f"entry {i} {name!r} exceeds input bounds")
        payload = raw[data_off:data_off + size]
        calc = crc16(payload)
        entries.append({
            "slot": i, "type": etype, "index": index, "name": name,
            "data_offset": data_off, "size": size,
            "stored_data_crc16_le": f"0x{stored_crc:04x}",
            "crc16_raw_payload": f"0x{calc:04x}",
            "raw_payload_crc_matches": stored_crc == calc,
            "raw_sha256": hashlib.sha256(payload).hexdigest(),
            "crc_scope_status": "raw_match" if stored_crc == calc else "raw_mismatch_scope_unresolved",
        })
        if etype == 0 or name == "flash.bin":
            flash_entry = (stored_crc, data_off, size, payload)
    if flash_entry is None:
        raise ValueError("no flash.bin entry found")

    _, flash_off, flash_size, flash = flash_entry
    flash_header_raw = flash[:0x20]
    if len(flash_header_raw) != 0x20:
        raise ValueError("flash.bin is too short for the 32-byte flash header")
    flash_header_plain = enc(flash_header_raw)
    stored_flash_hcrc = int.from_bytes(flash_header_plain[:2], "little")
    calculated_flash_hcrc = crc16(flash_header_plain[2:0x20])
    # Firmware display tools restore VID/PID bytes only AFTER this CRC check.
    display_view = bytearray(flash_header_plain)
    display_view[4:8] = flash_header_raw[4:8]
    display_view[16:32] = flash_header_raw[16:32]
    display_view_crc = crc16(display_view[2:0x20])

    # Decode top-level JLFS entry headers; the SPL is the first record at 0x20.
    top_entries = []
    cursor = 0x20
    spl = None
    for ordinal in range(64):
        if cursor + 0x20 > len(flash):
            raise ValueError("top-level JLFS entry header exceeds flash.bin bounds")
        plain = enc(flash[cursor:cursor + 0x20])
        stored_hcrc, data_crc, rel_off, size, flags, reserved, idx, name_raw = struct.unpack(
            "<HHIIBBH16s", plain
        )
        name = entry_name(name_raw)
        calc_hcrc = crc16(plain[2:0x20])
        rec = {
            "header_offset": cursor, "name": name, "flags": flags, "index": idx,
            "stored_header_crc16_le": f"0x{stored_hcrc:04x}",
            "calculated_header_crc16": f"0x{calc_hcrc:04x}",
            "header_crc_matches": stored_hcrc == calc_hcrc,
            "data_offset": rel_off, "size": size,
            "stored_data_crc16_le": f"0x{data_crc:04x}",
        }
        top_entries.append(rec)
        if name == "uboot.boot":
            if rel_off > len(flash) or size > len(flash) - rel_off:
                raise ValueError("uboot.boot range exceeds flash.bin bounds")
            spl = (rec, flash[rel_off:rel_off + size])
        if idx != 0:
            break
        cursor += 0x20
    else:
        raise ValueError("top-level JLFS record count exceeded safety limit")
    if spl is None:
        raise ValueError("no top-level uboot.boot entry found")

    spl_rec, spl_raw = spl
    spl_raw_crc = crc16(spl_raw)
    spl_dec = bytearray(spl_raw)
    if len(spl_dec) < 16:
        raise ValueError("uboot.boot too short for bankcb header")
    spl_dec[:16] = enc(bytes(spl_dec[:16]))
    bank_hdr = bytes(spl_dec[:14])
    bank_header_crc_stored = int.from_bytes(spl_dec[14:16], "little")
    bank_header_crc_calc = crc16(bank_hdr)
    if bank_header_crc_stored != bank_header_crc_calc:
        bank_result = {
            "bank_header_crc_matches": False,
            "note": "Bank header CRC did not validate; bank fields were not used to transform payload.",
        }
    else:
        bank_id, bank_size, bank_load, bank_off, bank_crc = struct.unpack("<HHIIH", bank_hdr)
        within = bank_off <= len(spl_dec) and bank_size <= len(spl_dec) - bank_off
        bank_result = {
            "bank_header_crc_matches": True,
            "bank_header_crc16_le": f"0x{bank_header_crc_stored:04x}",
            "bank_header_crc16_calculated": f"0x{bank_header_crc_calc:04x}",
            "bank_id": bank_id, "bank_size": bank_size, "bank_load": f"0x{bank_load:x}",
            "bank_offset": bank_off, "bank_crc16_le": f"0x{bank_crc:04x}",
            "bank_range_within_payload": within,
        }
        if within:
            spl_dec[bank_off:bank_off + bank_size] = enc(bytes(spl_dec[bank_off:bank_off + bank_size]))
            body_crc = crc16(bytes(spl_dec[bank_off:bank_off + bank_size]))
            whole_crc = crc16(bytes(spl_dec))
            bank_result.update({
                "bank_body_crc16_calculated": f"0x{body_crc:04x}",
                "bank_body_crc_matches": body_crc == bank_crc,
                "whole_payload_crc16_after_bankcb": f"0x{whole_crc:04x}",
                "whole_payload_crc_matches_jlfs_entry": whole_crc == int(spl_rec["stored_data_crc16_le"], 16),
                "descrambled_sha256": hashlib.sha256(spl_dec).hexdigest(),
                "decompression_performed": False,
            })

    return {
        "input": str(path),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_size": len(raw),
        "crc16_parameters": {
            "name": "JieLi jl_crc16 / CRC-16-XMODEM-style",
            "polynomial": "0x1021", "initial": "0x0000", "refin": False,
            "refout": False, "xorout": "0x0000", "stored_field_endian": "little-endian",
        },
        "enc_parameters": {"key": "0xffff", "stream": "XOR LFSR, state reset on each call"},
        "ufw_header": {
            "declared_size": declared_size, "entry_count": count,
            "stored_crc16_le": f"0x{hcrc:04x}",
            "calculated_crc16": f"0x{header_check:04x}",
            "range": "decrypted bytes [0x02,0x40)", "matches": hcrc == header_check,
        },
        "ufw_entry_list": {
            "stored_crc16_le": f"0x{listcrc:04x}",
            "calculated_crc16": f"0x{list_check:04x}",
            "range": f"raw encrypted entry headers [0x40,0x{table_end:x})",
            "matches": listcrc == list_check,
        },
        "ufw_entries_raw_scope": entries,
        "flash_header": {
            "file_offset": flash_off, "raw_hex": flash_header_raw.hex(),
            "fully_decrypted_hex_for_crc": flash_header_plain.hex(),
            "stored_crc16_le": f"0x{stored_flash_hcrc:04x}",
            "calculated_crc16_before_vid_pid_restore": f"0x{calculated_flash_hcrc:04x}",
            "crc_range": "fully decrypted header bytes [0x02,0x20), before restoring visible VID/PID",
            "matches_before_restore": stored_flash_hcrc == calculated_flash_hcrc,
            "diagnostic_crc_after_vid_pid_restore": f"0x{display_view_crc:04x}",
            "note": "Restored VID/PID bytes are a display/parsing view and are not the CRC input.",
        },
        "jlfs_top_entries": top_entries,
        "uboot_bankcb": {
            "stored_jlfs_data_crc16_le": spl_rec["stored_data_crc16_le"],
            "raw_payload_crc16": f"0x{spl_raw_crc:04x}",
            "raw_payload_crc_matches": spl_raw_crc == int(spl_rec["stored_data_crc16_le"], 16),
            "flags": spl_rec["flags"],
            "compression_flag_bit6_set": bool(spl_rec["flags"] & 0x40),
            "documented_codec": "LZ4" if spl_rec["flags"] & 0x40 else None,
            "documented_codec_source": "https://kagaimiq.github.io/jielie/datafmt/newfw.html",
            "bankcb": bank_result,
            "note": "The public format specification identifies LZ4 for bit 0x40; this audit performs bankcb descrambling and CRC checks only, not LZ4 decompression.",
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, help="Write JSON report; refuses to overwrite an existing file")
    args = ap.parse_args()
    report = audit(args.input)
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        if args.out.exists():
            raise FileExistsError(f"refusing to overwrite: {args.out}")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
