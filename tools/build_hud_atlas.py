#!/usr/bin/env python3
"""Build the current TOSTRTA LayeredFS HUD atlas.

The USA Rev 1 hud_all00.ctxb is RGBA4444, 256x256, Morton-swizzled in
8x8 tiles with a 72-byte CTXB header. This builder starts from the bundled
base resource, modifies the native English contextual-action word area plus
the verified alpha-zero injection rectangle, and writes the game-ready CTXB
plus a preview PNG.

The current builder keeps the project font resources, replaces the native English
contextual A-action word cells with project-font equivalents while preserving
the game's native dynamic selector, and leaves the native dive-depth selector
padding untouched. Button chrome/D-pad assets live in menu_top_parts00 so this
atlas cannot contaminate the native 6/7/8 Gold Scale depth cells.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageFilter
from ui_font import sprite as font_sprite

WIDTH = 256
HEIGHT = 256
HEADER_SIZE = 72
INJECT = (118, 184, 216, 256)  # verified alpha-zero in vanilla
# Native depth digits 6/7/8 use 64x18 selector cells at x=192..255 in the
# same rows as Jump/Save, Decide/Talk and Dive/Next. Their visible glyphs are
# near x=216, but the full selector quads also sample the transparent padding
# to the left. That padding MUST remain byte/pixel-equivalent to vanilla.
DIVE_COUNTER_CELLS = (192, 184, 256, 238)
ACTION_TEXT_RECT = (0, 94, 192, 256)  # enclosing area for native action words
ACTION_WORD_ROWS = (
    ("Attack", "Throw", "Quit"),
    ("Check", "Navi", "Put Away"),
    ("Enter", "Climb", "Reel"),
    ("Return", "Drop", "Swap"),
    ("Open", "Down", "Equip"),
    ("Jump", "Save", None),
    ("Decide", "Talk", None),
    ("Dive", "Next", None),
    ("Faster", "Grab", None),
)

# Atlas allocation used by full_hud_relocator.c.
# Digits are 12x14 (five per row). Labels are 14px-high source sprites and
# display slightly smaller. Shell/D-pad retain native/approved resolution.
REGIONS = {
    "D0": (118, 184, 12, 14), "D1": (130, 184, 12, 14),
    "D2": (142, 184, 12, 14), "D3": (154, 184, 12, 14),
    "D4": (166, 184, 12, 14),
    "D5": (118, 198, 12, 14), "D6": (130, 198, 12, 14),
    "D7": (142, 198, 12, 14), "D8": (154, 198, 12, 14),
    "D9": (166, 198, 12, 14),

    # 1.1 HUD shortcut labels. These mirror the physical D-pad actions after
    # swapping Up<->Start and Down<->Select.
    "ITEMS": (118, 212, 42, 14),
    "X": (160, 212, 12, 14),
    "Y": (172, 212, 12, 14),
    "GEAR": (118, 226, 30, 14),
    "LT": (148, 226, 14, 14),
    "RT": (162, 226, 14, 14),

    # Final row is outside the native dive-depth selector rows.
    "LB": (118, 240, 19, 14),
    "RB": (137, 240, 19, 14),
    "T": (156, 240, 11, 14),
    "B": (167, 240, 11, 14),
    "A": (178, 240, 12, 14),
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


def harden(source: Image.Image, alpha_threshold: int = 48,
           luminance_threshold: int = 96) -> Image.Image:
    """Hard black/white conversion used only for non-font outline artwork."""
    src = source.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    si = src.load()
    oi = out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = si[x, y]
            if a < alpha_threshold:
                continue
            lum = (r * 3 + g * 6 + b) // 10
            oi[x, y] = (255, 255, 255, 255) if lum >= luminance_threshold \
                        else (0, 0, 0, 255)
    return out


def white_fill_mask(source: Image.Image) -> Image.Image:
    """Recover only the white glyph fill from the project raster source.

    Older source PNGs may contain a large opaque black backing around the
    glyph. Ignoring dark source pixels and rebuilding the outline from the
    white fill prevents that backing from becoming a visible rectangle.
    """
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
            # Preserve antialias coverage from the bright fill while rejecting
            # the black source background/outline.
            coverage = (lum - 80) * 255 // 175
            if coverage > 255:
                coverage = 255
            coverage = coverage * a // 255
            oi[x, y] = coverage
    return out


def glyph_sprite(source: Image.Image, width: int, height: int,
                  margin: int = 1) -> Image.Image:
    """Create a clean white-fill/black-outline glyph cell.

    The cell is intentionally larger than the destination quad.  We retain
    alpha gradients in RGBA4444 and let the native board sampler reduce the
    cell at draw time, improving small-text smoothness without increasing the
    visible HUD label size.
    """
    mask = white_fill_mask(source)
    box = mask.getbbox()
    if box is None:
        raise ValueError("empty glyph fill")
    mask = mask.crop(box)

    available_w = max(1, width - margin * 2)
    available_h = max(1, height - margin * 2)
    ratio = min(available_w / mask.width, available_h / mask.height)
    out_w = max(1, min(available_w, round(mask.width * ratio)))
    out_h = max(1, min(available_h, round(mask.height * ratio)))
    fill = mask.resize((out_w, out_h), Image.Resampling.LANCZOS)

    fill_cell = Image.new("L", (width, height), 0)
    x = (width - out_w) // 2
    y = (height - out_h) // 2
    fill_cell.paste(fill, (x, y))

    # One atlas-pixel black outline at this higher source resolution. A tiny
    # blur only affects alpha coverage at the edge and survives RGBA4444 as a
    # controlled antialias rather than a hard staircase.
    outline = fill_cell.filter(ImageFilter.MaxFilter(3))
    outline = outline.filter(ImageFilter.GaussianBlur(0.25))

    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    black = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    black.putalpha(outline)
    result.alpha_composite(black)

    white = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    white.putalpha(fill_cell)
    result.alpha_composite(white)
    return result


def paste_region(atlas: Image.Image, name: str, sprite: Image.Image) -> None:
    x, y, w, h = REGIONS[name]
    if sprite.size != (w, h):
        raise ValueError(f"{name}: expected {(w, h)}, got {sprite.size}")
    atlas.alpha_composite(sprite, (x, y))


def build(base_path: Path, assets: Path, output: Path, preview: Path | None) -> None:
    base = base_path.read_bytes()
    atlas = decode_ctxb(base)

    # Safety: the complete allocation rectangle must be alpha-zero in vanilla.
    alpha = atlas.getchannel("A")
    if alpha.crop(INJECT).getbbox() is not None:
        raise RuntimeError("verified injection region is no longer transparent in base CTXB")

    vanilla = atlas.copy()
    atlas.paste((0, 0, 0, 0), INJECT)

    # Preserve the native contextual-action selector and its exact UV geometry,
    # but replace each English word inside the vanilla word bounds.  We do not
    # clear whole 64x18 cells because the lower rows border the transparent
    # injection rectangle used by TOSTRTA assets.
    action_words = Image.open(assets / "custom_ACTION_WORDS.png").convert("RGBA")
    if action_words.size != (192, 162):
        raise ValueError("unexpected action-word sheet dimensions")
    for row, names in enumerate(ACTION_WORD_ROWS):
        for col, name in enumerate(names):
            if name is None:
                continue
            cell_x = col * 64
            cell_y = 94 + row * 18
            vanilla_cell = vanilla.crop((cell_x, cell_y, cell_x + 64, cell_y + 18))
            target_box = vanilla_cell.getchannel("A").getbbox()
            if target_box is None:
                raise RuntimeError(f"missing vanilla action word cell: {name}")

            source_cell = font_sprite(name,64,18)
            source_box = source_cell.getchannel("A").getbbox()
            if source_box is None:
                raise RuntimeError(f"missing custom action word cell: {name}")
            sprite = source_cell.crop(source_box)

            tx0 = cell_x + target_box[0]
            ty0 = cell_y + target_box[1]
            tw = target_box[2] - target_box[0]
            th = target_box[3] - target_box[1]
            if sprite.size != (tw, th):
                sprite = font_sprite(name,tw,th)
            atlas.paste((0, 0, 0, 0), (tx0, ty0, tx0 + tw, ty0 + th))
            atlas.alpha_composite(sprite, (tx0, ty0))

    digit_sheet = Image.open(assets / "custom_DIGITS.png").convert("RGBA")
    if digit_sheet.size != (280, 32):
        raise ValueError("unexpected digit-sheet dimensions")
    for digit in range(10):
        cell = digit_sheet.crop((digit * 28, 0, (digit + 1) * 28, 32))
        _, _, w, h = REGIONS[f"D{digit}"]
        paste_region(atlas, f"D{digit}", font_sprite(str(digit),w,h))

    for name, filename in [
        ("X", "custom_X.png"), ("Y", "custom_Y.png"), ("B", "custom_B.png"),
        ("LB", "custom_LB.png"), ("RB", "custom_RB.png"),
        ("T", "custom_T.png"), ("A", "custom_A.png"),
        ("ITEMS", "custom_MAP.png"), ("GEAR", "custom_PAUSE.png"),
    ]:
        _, _, w, h = REGIONS[name]
        paste_region(atlas, name, font_sprite(name,w,h))
    for name in ('LT','RT'):
        _,_,w,h=REGIONS[name]
        paste_region(atlas,name,font_sprite(name,w,h))

    # Alpha-092 moves the shared shell and D-pad to menu_top_parts00. Keeping
    # this atlas clear in the fourth selector column prevents the native Gold
    # Scale depth counter from sampling custom pixels for values 6, 7 and 8.
    if atlas.crop(DIVE_COUNTER_CELLS) != vanilla.crop(DIVE_COUNTER_CELLS):
        raise RuntimeError("native dive-counter selector cells were modified")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encode_ctxb(base[:HEADER_SIZE], atlas))

    generated = output.read_bytes()
    verify = decode_ctxb(generated)
    if encode_ctxb(generated[:HEADER_SIZE], verify) != generated:
        raise RuntimeError("CTXB round-trip verification failed")

    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True)
        preview_img = verify.crop((110, 176, 224, 256)).resize(
            (456, 320), Image.Resampling.NEAREST)
        preview_img.save(preview)


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
