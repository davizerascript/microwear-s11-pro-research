#!/usr/bin/env python3
"""Read-only decoder for the compact SYS_CFG_PARAM payload embedded in JLFS isd_config.ini."""
from __future__ import annotations
import argparse, json
from pathlib import Path

MAX_INPUT_BYTES = 64 * 1024
MAX_RECORDS = 256


def decode(data: bytes) -> dict:
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError(f'payload excede limite de {MAX_INPUT_BYTES} bytes')
    if len(data) < 34:
        raise ValueError('payload menor que 34 bytes; cabeçalho binário esperado ausente')
    pos = 34  # first 32 bytes are an opaque key blob, followed by 2 opaque check bytes
    records = []
    while pos < len(data):
        value_len = data[pos]
        pos += 1
        key_end = data.find(b'\0', pos, min(len(data), pos + 65))
        if key_end < 0:
            raise ValueError(f'chave sem NUL ou maior que 64 bytes no offset 0x{pos:x}')
        key_raw = data[pos:key_end]
        if not key_raw or any(c < 0x20 or c > 0x7e for c in key_raw):
            raise ValueError(f'chave não ASCII imprimível no offset 0x{pos:x}')
        key = key_raw.decode('ascii')
        pos = key_end + 1
        end = pos + value_len
        if end > len(data):
            raise ValueError(f'valor de {key} extrapola o arquivo')
        value = data[pos:end]
        pos = end
        record = {'key': key, 'length': value_len, 'hex': value.hex()}
        try:
            text = value.decode('ascii')
            if all(0x20 <= ord(ch) <= 0x7e for ch in text):
                record['text'] = text
        except UnicodeDecodeError:
            pass
        if value_len == 4 and 'text' not in record:
            record['uint32_le'] = int.from_bytes(value, 'little')
        records.append(record)
        if len(records) > MAX_RECORDS:
            raise ValueError(f'número de registros excede limite de {MAX_RECORDS}')
    if pos != len(data):
        raise ValueError('bytes sobrando após decodificação')
    return {
        'format': 'JieLi SYS_CFG_PARAM compact records (structure observed in this sample)',
        'opaque_prefix_bytes': 32,
        'opaque_check_bytes': 2,
        'records_offset': 34,
        'records': records,
        'warning': 'Campos e valores são decodificados, mas semântica/pinagem exige documentação da revisão da placa.'
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()
    result = decode(args.input.read_bytes())
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        output = args.output.expanduser()
        if output.is_symlink() or output.exists():
            raise FileExistsError(f'recusando sobrescrever saída existente: {output}')
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    else:
        print(encoded, end='')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
