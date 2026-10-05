#!/usr/bin/env python3
"""Build TOSTRTA's lower-screen controller-label atlas override.

USA Rev 1 /menu/01_US_ENGLISH/menu_top_parts00.ctxb is RGBA4444,
512x256, Morton-swizzled in 8x8 tiles with a 72-byte CTXB header.

Alpha-017 changes only the five native controller-label cells on the right
side of the lower screen.  The underlying native item slots and behavior are
untouched.  Final visible mapping is:

    native I  cell -> LB
    native X  cell -> Y
    native Y  cell -> X
    native B  cell -> B
    native II cell -> RB

All labels use the project font with the native yellow/black lower-screen
color treatment. Alpha-092 also stores the top-screen clean action shell and
D-pad in a guarded transparent region of this atlas, away from hud_all00's
native Gold Scale depth-counter selector cells.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageFilter

WIDTH = 512
HEIGHT = 256
HEADER_SIZE = 72

# These rectangles contain only the original yellow/black controller labels;
# neighboring item artwork begins outside them.  Coordinates are from the
# decoded USA Rev 1 menu_top_parts00 atlas.
CELLS = {
    "I":  (156, 125, 175, 142),
    "X":  (156, 142, 175, 158),
    "Y":  (156, 158, 175, 174),
    "B":  (156, 174, 175, 190),
    "II": (156, 190, 175, 207),
}

MAPPING = {
    "I":  "LB",
    "X":  "Y",
    "Y":  "X",
    "B":  "B",
    "II": "RB",
}

ASSET_FOR = {
    "LB": "custom_LB.png",
    "RB": "custom_RB.png",
    "X": "custom_X.png",
    "Y": "custom_Y.png",
    "B": "custom_B.png",
}

# Alpha-092 custom top-screen chrome allocation. This 72x42 guard rectangle is
# fully alpha-zero in the USA Rev 1 base atlas and sits well away from native
# artwork. Two transparent pixels are retained around/between the resources.
CHROME_GUARD = (382, 182, 454, 224)
CHROME_REGIONS = {
    "SHELL": (384, 184, 38, 38),
    "DPAD":  (424, 189, 28, 28),
}


def morton3(x: int, y: int) -> int:
    return ((x & 1) << 0) | ((y & 1) << 1) | ((x & 2) << 1) | \
           ((y & 2) << 2) | ((x & 4) << 2) | ((y & 4) << 3)


def decode_ctxb(data: bytes) -> Image.Image:
    if len(data) != HEADER_SIZE + WIDTH * HEIGHT * 2:
        raise ValueError(f"unexpected CTXB size: {len(data)}")
    if data[:4] != b"ctxb":
        raise ValueError("not a CTXB resource")
    tex = data[HEADER_SIZE:]
    out = Image.new("RGBA", (WIDTH, HEIGHT))
    px = out.load()
    tiles_per_row = WIDTH // 8
    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = (y // 8) * tiles_per_row + (x // 8)
            idx = tile * 64 + morton3(x & 7, y & 7)
            value = tex[idx * 2] | (tex[idx * 2 + 1] << 8)
            px[x, y] = (
                ((value >> 12) & 0xF) * 17,
                ((value >> 8) & 0xF) * 17,
                ((value >> 4) & 0xF) * 17,
                (value & 0xF) * 17,
            )
    return out


def q4(value: int) -> int:
    return max(0, min(15, (int(value) + 8) // 17))


def encode_ctxb(header: bytes, image: Image.Image) -> bytes:
    if image.size != (WIDTH, HEIGHT):
        raise ValueError("atlas dimensions changed")
    tex = bytearray(WIDTH * HEIGHT * 2)
    px = image.convert("RGBA").load()
    tiles_per_row = WIDTH // 8
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b, a = px[x, y]
            value = (q4(r) << 12) | (q4(g) << 8) | (q4(b) << 4) | q4(a)
            tile = (y // 8) * tiles_per_row + (x // 8)
            idx = tile * 64 + morton3(x & 7, y & 7)
            tex[idx * 2] = value & 0xFF
            tex[idx * 2 + 1] = value >> 8
    return header + bytes(tex)


def white_fill_mask(source: Image.Image) -> Image.Image:
    src = source.convert("RGBA")
    out = Image.new("L", src.size, 0)
    si = src.load()
    oi = out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = si[x, y]
            if a == 0:
                continue
            lum = max(r, g, b)
            if lum <= 80:
                continue
            coverage = min(255, (lum - 80) * 255 // 175)
            oi[x, y] = coverage * a // 255
    return out


def label_sprite(source: Image.Image, width: int, height: int) -> Image.Image:
    """Render project-font glyphs in native lower-screen yellow/black."""
    mask = white_fill_mask(source)
    box = mask.getbbox()
    if box is None:
        raise ValueError("empty label source")
    mask = mask.crop(box)

    # Leave one pixel for the outline.  LB/RB are deliberately allowed to use
    # almost the full cell width so they remain readable at native scale.
    aw = max(1, width - 2)
    ah = max(1, height - 2)
    ratio = min(aw / mask.width, ah / mask.height)
    out_w = max(1, min(aw, round(mask.width * ratio)))
    out_h = max(1, min(ah, round(mask.height * ratio)))
    fill = mask.resize((out_w, out_h), Image.Resampling.LANCZOS)

    fill_cell = Image.new("L", (width, height), 0)
    x = (width - out_w) // 2
    y = (height - out_h) // 2
    fill_cell.paste(fill, (x, y))

    outline = fill_cell.filter(ImageFilter.MaxFilter(3))
    outline = outline.filter(ImageFilter.GaussianBlur(0.20))

    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    black = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    black.putalpha(outline)
    result.alpha_composite(black)

    yellow = Image.new("RGBA", (width, height), (255, 255, 0, 0))
    yellow.putalpha(fill_cell)
    result.alpha_composite(yellow)
    return result


def build(base_path: Path, assets: Path, output: Path, preview: Path | None) -> None:
    base = base_path.read_bytes()
    atlas = decode_ctxb(base)
    original = atlas.copy()

    # The entire custom-chrome guard must be genuinely transparent in the
    # vanilla resource. This fails closed if a future base atlas differs.
    if original.getchannel("A").crop(CHROME_GUARD).getbbox() is not None:
        raise RuntimeError("custom chrome guard is not transparent in base CTXB")

    for native_name, replacement in MAPPING.items():
        x0, y0, x1, y1 = CELLS[native_name]
        # Safety: every opaque vanilla pixel in these cells must be yellow-ish
        # or black. This keeps the patch from accidentally erasing adjacent
        # native item artwork if the resource ever changes.
        cell = original.crop((x0, y0, x1, y1))
        for r, g, b, a in cell.get_flattened_data():
            if a == 0:
                continue
            is_black = r <= 17 and g <= 17 and b <= 17
            is_yellow = r >= 34 and g >= 34 and b <= 17
            if not (is_black or is_yellow):
                raise RuntimeError(f"unexpected non-label pixel in {native_name} cell")

        atlas.paste((0, 0, 0, 0), (x0, y0, x1, y1))
        sprite = label_sprite(Image.open(assets / ASSET_FOR[replacement]), x1 - x0, y1 - y0)
        atlas.alpha_composite(sprite, (x0, y0))

    shell = Image.open(assets / "native_A_shell_clean_38x38.png").convert("RGBA")
    sx, sy, sw, sh = CHROME_REGIONS["SHELL"]
    if shell.size != (sw, sh):
        raise ValueError("unexpected clean-shell dimensions")
    atlas.alpha_composite(shell, (sx, sy))

    dpad = Image.open(assets / "custom_DPAD.png").convert("RGBA")
    dx, dy, dw, dh = CHROME_REGIONS["DPAD"]
    if dpad.size != (dw, dh):
        dpad = dpad.resize((dw, dh), Image.Resampling.LANCZOS)
    atlas.alpha_composite(dpad, (dx, dy))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encode_ctxb(base[:HEADER_SIZE], atlas))

    verify = decode_ctxb(output.read_bytes())
    if encode_ctxb(output.read_bytes()[:HEADER_SIZE], verify) != output.read_bytes():
        raise RuntimeError("CTXB round-trip verification failed")

    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True)
        # Show both the native lower-screen label strip and the guarded custom
        # chrome block used by the top-screen HUD.
        labels = verify.crop((140, 116, 190, 216)).resize((300, 600), Image.Resampling.NEAREST)
        chrome = verify.crop((378, 178, 458, 228)).resize((480, 300), Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", (780, 600), (0, 0, 0, 0))
        canvas.alpha_composite(labels, (0, 0))
        canvas.alpha_composite(chrome, (300, 0))
        canvas.save(preview)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    build(args.base, args.assets, args.output, args.preview)


if __name__ == "__main__":
    main()
