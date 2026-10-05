#!/usr/bin/env python3
"""Build the Alpha-060 active Ocarina staff presentation remap.

OoT3D's top-screen/message Ocarina staff does not use the localized
menu_okarina_parts00.ctxb sheet atlas.  It uses the five-note strip in
rom:/message/parts.ctxb instead.  That strip is the contiguous 16x16 set at
Y=48, ordered L / R / Y / X / A and intentionally contains no B entry.

Alpha-060 keeps the proven active/live five-note strip mapping unchanged:

    native L -> LT
    native R -> RT
    native Y -> X
    native X -> Y
    native A -> B

The canonical twelve-song table is never modified. Fixed-song success/playback
presentation is translated only at its render consumer. Learned-song sheets use
the separate menu atlas, where Alpha-060 swaps only the staff X/Y artwork to
match the same physical Xbox labels. Neither resource changes pitch or song
recognition semantics.

The general message/controller glyph set at Y=32 is left untouched, so ordinary
A/B/X/Y/L/R prompts elsewhere in the game keep their vanilla labels.  The B
sprite copied into the Ocarina A slot comes from that untouched general set.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 256
HEIGHT = 128
HEADER_SIZE = 72
CELL = 16
OCARINA_Y = 48
GENERAL_Y = 32
OCARINA_CELLS = {
    "L": 0,
    "R": 16,
    "Y": 32,
    "X": 48,
    "A": 64,
}
GENERAL_B_X = 144


def morton8(x: int, y: int) -> int:
    value = 0
    for bit in range(3):
        value |= ((x >> bit) & 1) << (bit * 2)
        value |= ((y >> bit) & 1) << (bit * 2 + 1)
    return value


def pixel_offset(x: int, y: int) -> int:
    tiles_per_row = WIDTH // 8
    tile = (y // 8) * tiles_per_row + (x // 8)
    pixel = tile * 64 + morton8(x & 7, y & 7)
    return HEADER_SIZE + pixel * 2


def decode_pixel(raw: bytes) -> tuple[int, int, int, int]:
    value = int.from_bytes(raw, "little")
    return (
        ((value >> 12) & 0xF) * 17,
        ((value >> 8) & 0xF) * 17,
        ((value >> 4) & 0xF) * 17,
        (value & 0xF) * 17,
    )


def encode_pixel(rgba: tuple[int, int, int, int]) -> bytes:
    q = [max(0, min(15, int(round(c / 17.0)))) for c in rgba]
    value = (q[0] << 12) | (q[1] << 8) | (q[2] << 4) | q[3]
    return value.to_bytes(2, "little")


def decode_ctxb(data: bytes) -> Image.Image:
    if len(data) != HEADER_SIZE + WIDTH * HEIGHT * 2:
        raise ValueError(f"unexpected message parts CTXB size: {len(data)}")
    if data[:4] != b"ctxb":
        raise ValueError("not a CTXB resource")
    image = Image.new("RGBA", (WIDTH, HEIGHT))
    px = image.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            off = pixel_offset(x, y)
            px[x, y] = decode_pixel(data[off:off + 2])
    return image


def write_cell(data: bytearray, image: Image.Image, x0: int, y0: int) -> None:
    px = image.convert("RGBA").load()
    for y in range(CELL):
        for x in range(CELL):
            off = pixel_offset(x0 + x, y0 + y)
            data[off:off + 2] = encode_pixel(px[x, y])


def copy_cell(original: bytes, data: bytearray,
              src_x: int, src_y: int, dst_x: int, dst_y: int) -> None:
    # Copy decoded RGBA4 pixels rather than assuming the two cells share the
    # same swizzled tile alignment.  Encoding is lossless for native RGBA4.
    source = decode_ctxb(original).crop((src_x, src_y, src_x + CELL, src_y + CELL))
    write_cell(data, source, dst_x, dst_y)


def make_trigger_cell(original: Image.Image, x0: int, text: str) -> Image.Image:
    source = original.crop((x0, OCARINA_Y, x0 + CELL, OCARINA_Y + CELL)).convert("RGBA")
    alpha = source.getchannel("A")

    # Retain the native small rectangular trigger shell while replacing only
    # the center ink. This matches the LT/RT treatment already accepted on the
    # song sheet, but uses the message atlas' own RGBA4 shell.
    rgb = source.convert("RGB")
    pale = rgb.filter(ImageFilter.MaxFilter(5))
    rgb.paste(pale.crop((3, 2, 14, 14)), (3, 2))
    cell = Image.merge("RGBA", (*rgb.split(), alpha))

    font = ImageFont.load_default(size=8)
    draw = ImageDraw.Draw(cell)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = (CELL - width) // 2 - bbox[0]
    y = (CELL - height) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(24, 24, 24, 255))

    # The shell's original alpha is authoritative. Text is drawn entirely
    # inside its opaque region, so restoring alpha avoids changing silhouette.
    cell.putalpha(alpha)
    return cell


def build(base_path: Path, output: Path, preview: Path | None) -> None:
    original_bytes = base_path.read_bytes()
    if len(original_bytes) != HEADER_SIZE + WIDTH * HEIGHT * 2:
        raise ValueError(f"unexpected base size: {len(original_bytes)}")
    raw = bytearray(original_bytes)
    original = decode_ctxb(original_bytes)

    # Active staff's native A note becomes the Xbox B note. Use the untouched
    # general-message B cell as the pixel source; do not alter that source cell.
    copy_cell(original_bytes, raw,
              GENERAL_B_X, GENERAL_Y,
              OCARINA_CELLS["A"], OCARINA_Y)

    # Native X/Y glyphs remain unchanged.

    # Active staff L/R notes become LT/RT.
    write_cell(raw, make_trigger_cell(original, OCARINA_CELLS["L"], "LT"),
               OCARINA_CELLS["L"], OCARINA_Y)
    write_cell(raw, make_trigger_cell(original, OCARINA_CELLS["R"], "RT"),
               OCARINA_CELLS["R"], OCARINA_Y)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raw)

    if preview:
        verify = decode_ctxb(bytes(raw))
        preview.parent.mkdir(parents=True, exist_ok=True)
        # Show the untouched general set above the corrected five-note strip.
        verify.crop((0, 28, 224, 68)).resize((1344, 240), Image.Resampling.NEAREST).save(preview)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    build(args.base, args.output, args.preview)
