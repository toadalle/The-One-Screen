#!/usr/bin/env python3
"""Preserve native Ocarina artwork while adapting controller lettering.
USA-English 512x256 ETC1A4. X/Y and the shared A0 note cell are unchanged.
The learned-song A1 cell uses B; L/R color blocks carry LT/RT. The native red
Quit container stays untouched; main uses the existing HUD A bubble.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from ui_font import sprite as font_sprite

WIDTH = 512
HEIGHT = 256
HEADER_SIZE = 72
CELL_Y = 160
NOTE_CELLS = {
    # The atlas carries two native A variants before B/X/Y/L/R. A0 is shared
    # with colorful song-note art, so only the staff-note A1 cell is patched.
    "A0": 128,
    "A1": 144,
    "B": 160,
    "X": 176,
    "Y": 192,
    "L": 208,
    "R": 224,
}

MODIFIERS = (
    (2, 8, -2, -8),
    (5, 17, -5, -17),
    (9, 29, -9, -29),
    (13, 42, -13, -42),
    (18, 60, -18, -60),
    (24, 80, -24, -80),
    (33, 106, -33, -106),
    (47, 183, -47, -183),
)


def morton2(x: int, y: int) -> int:
    return (x & 1) | ((y & 1) << 1)


def block_index(bx: int, by: int) -> int:
    blocks_per_row = WIDTH // 4
    tx, ty = bx // 2, by // 2
    ix, iy = bx & 1, by & 1
    return (ty * (blocks_per_row // 2) + tx) * 4 + morton2(ix, iy)


def clamp(v: int) -> int:
    return 0 if v < 0 else 255 if v > 255 else v


def expand4(v: int) -> int:
    return (v << 4) | v


def decode_color(block: bytes) -> list[tuple[int, int, int]]:
    """Decode the PICA ETC1 color half used by this resource."""
    value = int.from_bytes(block, "little")
    high = (value >> 32) & 0xFFFFFFFF
    low = value & 0xFFFFFFFF
    diff = (high >> 1) & 1
    flip = high & 1
    table1 = (high >> 5) & 7
    table2 = (high >> 2) & 7

    if diff:
        def s3(x: int) -> int:
            return x - 8 if x & 4 else x
        def e5(x: int) -> int:
            return (x << 3) | (x >> 2)
        r1 = (high >> 27) & 31
        g1 = (high >> 19) & 31
        b1 = (high >> 11) & 31
        r2 = (r1 + s3((high >> 24) & 7)) & 31
        g2 = (g1 + s3((high >> 16) & 7)) & 31
        b2 = (b1 + s3((high >> 8) & 7)) & 31
        c1 = (e5(r1), e5(g1), e5(b1))
        c2 = (e5(r2), e5(g2), e5(b2))
    else:
        c1 = (expand4((high >> 28) & 15),
              expand4((high >> 20) & 15),
              expand4((high >> 12) & 15))
        c2 = (expand4((high >> 24) & 15),
              expand4((high >> 16) & 15),
              expand4((high >> 8) & 15))

    out: list[tuple[int, int, int]] = [(0, 0, 0)] * 16
    for y in range(4):
        for x in range(4):
            k = x * 4 + y
            idx = ((low >> k) & 1) | (((low >> (k + 16)) & 1) << 1)
            second = (y >= 2) if flip else (x >= 2)
            base = c2 if second else c1
            table = table2 if second else table1
            m = MODIFIERS[table][idx]
            out[y * 4 + x] = tuple(clamp(c + m) for c in base)
    return out


def decode_alpha(block: bytes) -> list[int]:
    value = int.from_bytes(block, "little")
    out = [0] * 16
    for y in range(4):
        for x in range(4):
            k = y * 4 + x
            out[y * 4 + x] = ((value >> (k * 4)) & 0xF) * 17
    return out


def decode_ctxb(data: bytes) -> Image.Image:
    if len(data) != HEADER_SIZE + WIDTH * HEIGHT:
        raise ValueError(f"unexpected Ocarina CTXB size: {len(data)}")
    if data[:4] != b"ctxb":
        raise ValueError("not a CTXB resource")
    tex = data[HEADER_SIZE:]
    image = Image.new("RGBA", (WIDTH, HEIGHT))
    px = image.load()
    for by in range(HEIGHT // 4):
        for bx in range(WIDTH // 4):
            offset = block_index(bx, by) * 16
            raw = tex[offset:offset + 16]
            alpha = decode_alpha(raw[:8])
            color = decode_color(raw[8:])
            for y in range(4):
                for x in range(4):
                    r, g, b = color[y * 4 + x]
                    px[bx * 4 + x, by * 4 + y] = (r, g, b, alpha[y * 4 + x])
    return image


def quant4(v: float) -> int:
    return max(0, min(15, int(round(v / 17.0))))


def block_error(pixels, base, table):
    total = 0
    indices = []
    for r, g, b in pixels:
        best_i = 0
        best_e = 1 << 60
        for i, mod in enumerate(MODIFIERS[table]):
            rr = clamp(base[0] + mod)
            gg = clamp(base[1] + mod)
            bb = clamp(base[2] + mod)
            e = (r - rr) ** 2 + (g - gg) ** 2 + (b - bb) ** 2
            if e < best_e:
                best_e, best_i = e, i
        total += best_e
        indices.append(best_i)
    return total, indices


def encode_subblock(coords, rgb):
    vals = [rgb[y * 4 + x] for x, y in coords]
    means = tuple(sum(p[c] for p in vals) / len(vals) for c in range(3))
    q = [quant4(v) for v in means]
    best = None
    # Small local search around mean 4-bit base. Text/button blocks are simple,
    # so individual ETC1 mode is sufficient and preserves the native look.
    for dr in (-1, 0, 1):
        for dg in (-1, 0, 1):
            for db in (-1, 0, 1):
                qr = max(0, min(15, q[0] + dr))
                qg = max(0, min(15, q[1] + dg))
                qb = max(0, min(15, q[2] + db))
                base = (expand4(qr), expand4(qg), expand4(qb))
                for table in range(8):
                    err, indices = block_error(vals, base, table)
                    candidate = (err, qr, qg, qb, table, indices)
                    if best is None or candidate[0] < best[0]:
                        best = candidate
    assert best is not None
    return best


def encode_color(rgb: list[tuple[int, int, int]]) -> bytes:
    best_full = None
    for flip in (0, 1):
        if flip:
            c1 = [(x, y) for y in range(2) for x in range(4)]
            c2 = [(x, y) for y in range(2, 4) for x in range(4)]
        else:
            c1 = [(x, y) for y in range(4) for x in range(2)]
            c2 = [(x, y) for y in range(4) for x in range(2, 4)]
        a = encode_subblock(c1, rgb)
        b = encode_subblock(c2, rgb)
        total = a[0] + b[0]
        if best_full is None or total < best_full[0]:
            best_full = (total, flip, c1, c2, a, b)

    _, flip, c1, c2, a, b = best_full
    _, r1, g1, b1, t1, idx1 = a
    _, r2, g2, b2, t2, idx2 = b
    # Individual mode: R1 R2 G1 G2 B1 B2 table1 table2 diff=0 flip.
    high = ((r1 & 15) << 28) | ((r2 & 15) << 24) | \
           ((g1 & 15) << 20) | ((g2 & 15) << 16) | \
           ((b1 & 15) << 12) | ((b2 & 15) << 8) | \
           ((t1 & 7) << 5) | ((t2 & 7) << 2) | (flip & 1)
    low = 0
    for coords, indices in ((c1, idx1), (c2, idx2)):
        for (x, y), idx in zip(coords, indices):
            k = x * 4 + y
            low |= (idx & 1) << k
            low |= ((idx >> 1) & 1) << (k + 16)
    return ((high << 32) | low).to_bytes(8, "little")


def copy_cell_bytes(source: bytes, data: bytearray, src_x: int, dst_x: int) -> None:
    source_blocks = []
    for y in range(0, 16, 4):
        for x in range(0, 16, 4):
            source_blocks.append(bytes(source[
                HEADER_SIZE + block_index((src_x + x) // 4, (CELL_Y + y) // 4) * 16:
                HEADER_SIZE + block_index((src_x + x) // 4, (CELL_Y + y) // 4) * 16 + 16
            ]))
    n = 0
    for y in range(0, 16, 4):
        for x in range(0, 16, 4):
            off = HEADER_SIZE + block_index((dst_x + x) // 4, (CELL_Y + y) // 4) * 16
            data[off:off + 16] = source_blocks[n]
            n += 1


def make_trigger_cell(original: Image.Image, x0: int, text: str) -> Image.Image:
    cell = original.crop((x0, CELL_Y, x0 + 16, CELL_Y + 16)).convert("RGBA")
    # Remove the old single-letter ink while retaining the native rectangular
    # button shell. A max filter supplies nearby pale shell texels over only the
    # central label area; the dark bevel/border remains untouched.
    rgb = cell.convert("RGB")
    pale = rgb.filter(ImageFilter.MaxFilter(5))
    cell.paste(pale.crop((3, 2, 14, 14)), (3, 2))

    # Compact two-character trigger text. DejaVu Sans Condensed Bold closely
    # matches the native button's heavy small-cap proportions at this size.
    font = ImageFont.load_default(size=8)
    draw = ImageDraw.Draw(cell)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (16 - tw) // 2 - bbox[0]
    y = (16 - th) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(24, 24, 24, 255))
    return cell


def replace_cell_color(data: bytearray, target: Image.Image, x0: int) -> None:
    px = target.convert("RGB").load()
    for y0 in range(0, 16, 4):
        for xoff in range(0, 16, 4):
            rgb = []
            for y in range(4):
                for x in range(4):
                    rgb.append(px[xoff + x, y0 + y])
            off = HEADER_SIZE + block_index((x0 + xoff) // 4, (CELL_Y + y0) // 4) * 16
            # Preserve the original ETC1A4 alpha half exactly.
            data[off + 8:off + 16] = encode_color(rgb)


# The 108-quad native full-size Ocarina has a DIFFERENT glyph family at
# y=232. Its UV table contains these exact origins (19x22): L/R/X/Y/A.
# Do not modify the small staff glyphs or color-note art to relabel these.
FULL_GLYPHS = ((392, "LT"), (416, "RT"), (440, "X"), (464, "Y"), (488, "B"))


def clear_full_label(data: bytearray, x0: int) -> None:
    """Remove only the dedicated native full-size play letters (ETC1A4).

    Preserve neighboring artwork, every color block, small staff glyphs,
    and all control/button chrome. The sole replacement text now comes
    from the existing project glyph scene in the native draw hook.
    """
    for y in range(232, 256, 4):
        for x in range(x0, x0 + 20, 4):
            off = HEADER_SIZE + block_index(x//4, y//4) * 16
            data[off:off+8] = b"\x00" * 8


QUIT_LETTER_BLOCKS = (76, 164, 88, 176)


def replace_native_quit_letter(data: bytearray, original: Image.Image) -> None:
    """Keep the native red Quit card, beige bubble and alpha; repair baked B.

    Native Ocarina quads 34/57 share this Quit-card atlas region. Only its
    small letter (within a 12x12 set of ETC blocks) is altered to Xbox A.
    """
    from ui_font import FONT
    x0, y0, x1, y1 = QUIT_LETTER_BLOCKS
    cell = original.crop((x0, y0, x1, y1)).convert('RGBA')
    d = ImageDraw.Draw(cell)
    # x=80..86,y=166..173 inside the inherited ivory native button.
    d.rectangle((4, 2, 10, 9), fill=(225, 222, 192, 255))
    d.text((4, 0), 'A', font=ImageFont.truetype(str(FONT), 9), fill=(43, 42, 32, 255))
    px = cell.load()
    for by in range(0, 12, 4):
        for bx in range(0, 12, 4):
            rgb = [(px[bx+xx, by+yy][0],px[bx+xx, by+yy][1],px[bx+xx, by+yy][2])
                   for yy in range(4) for xx in range(4)]
            off=HEADER_SIZE+block_index((x0+bx)//4,(y0+by)//4)*16
            # No change to the inherited card's alpha/container geometry.
            data[off+8:off+16]=encode_color(rgb)


def build(base_path: Path, output: Path, preview: Path | None) -> None:
    raw = bytearray(base_path.read_bytes())
    if len(raw) != HEADER_SIZE + WIDTH * HEIGHT:
        raise ValueError(f"unexpected base size: {len(raw)}")
    original_bytes = bytes(raw)
    original = decode_ctxb(original_bytes)

    # The first A variant (A0) shares the edge used by the colorful song-note
    # sprites. Keep it byte-for-byte vanilla: replacing it caused a B-shaped
    # artifact to appear beside every colored note in the song list. Only A1
    # is the learned-song staff A glyph that should present as Xbox B.
    copy_cell_bytes(original_bytes, raw, NOTE_CELLS["B"], NOTE_CELLS["A1"])

    # Trigger labels need two characters, so preserve the native shells and
    # recompress only their 8-byte ETC1 color halves.
    # The original L/R rectangles are lighter than circular face-note sprites.
    # Lower the replacement shell/ink luminance while preserving the native
    # ETC1A4 alpha, outline, bevel, geometry and adjacent atlas blocks.
    lt = ImageEnhance.Brightness(make_trigger_cell(original, NOTE_CELLS["L"], "LT")).enhance(.76)
    rt = ImageEnhance.Brightness(make_trigger_cell(original, NOTE_CELLS["R"], "RT")).enhance(.76)
    replace_cell_color(raw, lt, NOTE_CELLS["L"])
    replace_cell_color(raw, rt, NOTE_CELLS["R"])

    # Isolated full-size native PLAY labels. X and Y stay their original glyphs;
    # the transient draw seam exchanges their entire button groups instead.
    # The FULL-SIZE glyph cells are independent of the small staff symbols.
    # Relabel them here, ONCE, instead of putting a second glyph layer over
    # retained native lettering. The live draw seam moves whole X/Y groups.
    for x0, name in FULL_GLYPHS:
        clear_full_label(raw, x0)
    replace_native_quit_letter(raw, original)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raw)

    verify = decode_ctxb(bytes(raw))
    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True)
        # Native staff button cells A/B/X/Y/L/R plus a little surrounding atlas.
        verify.crop((56, 148, 240, 196)).resize((1104, 288), Image.Resampling.NEAREST).save(preview)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    build(args.base, args.output, args.preview)
