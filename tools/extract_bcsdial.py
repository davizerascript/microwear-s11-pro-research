#!/usr/bin/env python3
"""Carve validated JPEG/BMP images and bounded gzip streams from a BCSDIAL blob."""
from __future__ import annotations
import argparse, gzip, hashlib, json, struct, zlib
from pathlib import Path
from io import BytesIO
from PIL import Image

MAX_IMAGE_DIM = 8192
MAX_GZIP_OUTPUT = 64 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_info(blob: bytes, fmt: str) -> tuple[int, int]:
    with Image.open(BytesIO(blob)) as im:
        if im.format != fmt:
            raise ValueError(f'Pillow detectou {im.format}, esperado {fmt}')
        w, h = im.size
        if not (1 <= w <= MAX_IMAGE_DIM and 1 <= h <= MAX_IMAGE_DIM):
            raise ValueError(f'dimensões implausíveis {w}x{h}')
        im.verify()
    return w, h


def extract(source: Path, output: Path) -> dict:
    data = source.read_bytes()
    if not data.startswith(b'BCSDIAL'):
        raise ValueError('assinatura BCSDIAL ausente')
    if len(data) < 0x44:
        raise ValueError('arquivo curto demais para os campos observados')

    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f'diretório de saída não vazio; escolha outro caminho: {output}')
    output.mkdir(parents=True, exist_ok=True)
    image_dir = output / 'images'
    stream_dir = output / 'gzip'
    image_dir.mkdir()
    stream_dir.mkdir()

    timestamp = data[7:21].decode('ascii', 'replace')
    header_value = struct.unpack_from('<I', data, 0x40)[0]
    images: list[dict] = []
    occupied: list[tuple[int, int]] = []

    # JPEG: require SOI/marker prefix, a complete EOI and successful Pillow verification.
    pos = 0
    index = 0
    while True:
        start = data.find(b'\xff\xd8\xff', pos)
        if start < 0:
            break
        end_marker = data.find(b'\xff\xd9', start + 3)
        if end_marker < 0:
            pos = start + 3
            continue
        end = end_marker + 2
        blob = data[start:end]
        try:
            width, height = image_info(blob, 'JPEG')
        except Exception:
            pos = start + 3
            continue
        index += 1
        name = f'jpeg_{index:03d}.jpg'
        (image_dir / name).write_bytes(blob)
        images.append({'name': name, 'format': 'JPEG', 'offset': start, 'end_exclusive': end,
                       'size': len(blob), 'width': width, 'height': height, 'sha256': sha256(blob)})
        occupied.append((start, end))
        pos = end

    # BMP: validate the file and DIB headers plus decodability; ignore false-positive BM markers.
    pos = 0
    bmp_index = 0
    while True:
        start = data.find(b'BM', pos)
        if start < 0:
            break
        pos = start + 2
        if any(a <= start < b for a, b in occupied) or start + 54 > len(data):
            continue
        declared = struct.unpack_from('<I', data, start + 2)[0]
        pixel_off = struct.unpack_from('<I', data, start + 10)[0]
        dib_size = struct.unpack_from('<I', data, start + 14)[0]
        width = struct.unpack_from('<i', data, start + 18)[0]
        height = struct.unpack_from('<i', data, start + 22)[0]
        planes = struct.unpack_from('<H', data, start + 26)[0]
        bpp = struct.unpack_from('<H', data, start + 28)[0]
        if (dib_size < 40 or declared < 54 or start + declared > len(data) or
            pixel_off < 14 + dib_size or pixel_off >= declared or planes != 1 or
            not (1 <= width <= MAX_IMAGE_DIM) or not (1 <= abs(height) <= MAX_IMAGE_DIM) or
            bpp not in (1, 4, 8, 16, 24, 32)):
            continue
        end = start + declared
        blob = data[start:end]
        try:
            iw, ih = image_info(blob, 'BMP')
        except Exception:
            continue
        bmp_index += 1
        name = f'bmp_{bmp_index:03d}.bmp'
        (image_dir / name).write_bytes(blob)
        images.append({'name': name, 'format': 'BMP', 'offset': start, 'end_exclusive': end,
                       'size': len(blob), 'width': iw, 'height': ih, 'bits_per_pixel': bpp,
                       'sha256': sha256(blob)})
        occupied.append((start, end))

    # Gzip: cap decompressed output to 64 MiB per stream; zlib validates gzip CRC/trailer.
    streams: list[dict] = []
    pos = 0
    while True:
        start = data.find(b'\x1f\x8b\x08', pos)
        if start < 0:
            break
        pos = start + 3
        if any(a <= start < b for a, b in occupied):
            continue
        dec = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            out = dec.decompress(data[start:], MAX_GZIP_OUTPUT + 1)
            if len(out) > MAX_GZIP_OUTPUT or dec.unconsumed_tail:
                streams.append({'offset': start, 'status': 'rejected_output_limit'})
                continue
            if not dec.eof:
                streams.append({'offset': start, 'status': 'incomplete_or_rejected'})
                continue
            consumed = len(data[start:]) - len(dec.unused_data)
            if consumed <= 0:
                streams.append({'offset': start, 'status': 'invalid_length'})
                continue
        except zlib.error as exc:
            streams.append({'offset': start, 'status': 'invalid_gzip', 'error': str(exc)[:160]})
            continue
        n = len([x for x in streams if x.get('status') == 'decoded']) + 1
        name = f'gzip_{n:03d}.bin'
        (stream_dir / name).write_bytes(out)
        streams.append({'name': name, 'status': 'decoded', 'offset': start,
                        'end_exclusive': start + consumed, 'compressed_size': consumed,
                        'output_size': len(out), 'output_magic_hex': out[:16].hex(),
                        'sha256': sha256(out)})
        pos = start + consumed

    manifest = {
        'source_name': source.name,
        'source_size': len(data),
        'source_sha256': sha256(data),
        'magic': 'BCSDIAL',
        'timestamp_text': timestamp,
        'observed_u32le_at_0x40': header_value,
        'observed_u32le_matches_file_size_minus_4': header_value == len(data) - 4,
        'format_semantics_confirmed': False,
        'images': sorted(images, key=lambda x: x['offset']),
        'gzip_streams': streams,
        'limitations': ['BCSDIAL header/record semantics are not publicly identified yet.',
                        'Embedded images were carved by signatures and validated by Pillow; their role in the dial is unknown.']
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    report = extract(args.input, args.out)
    print(json.dumps({'source_sha256': report['source_sha256'],
                      'images': len(report['images']),
                      'image_formats': {fmt: sum(1 for x in report['images'] if x['format'] == fmt)
                                        for fmt in sorted({x['format'] for x in report['images']})},
                      'gzip_streams': report['gzip_streams']}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
