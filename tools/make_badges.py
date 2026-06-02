#!/usr/bin/env python3
"""
make_badges.py - generate chip/pill-style tech badges as self-contained SVGs.

The text is OUTLINED to vector <path> data (no live font), so the chips render
identically in every browser and through GitHub's image proxy, in a modern font
(Inter), with zero font-loading dependency.

Usage:
    python make_badges.py OUT.svg "Label1=#rrggbb" "Label2=#rrggbb" [...]

Example:
    python make_badges.py assets/tags-cws.svg \
        "C=#555555" "Winsock2=#0078D4" "Win32 Threads=#2EA44F" "TCP Sockets=#E81F26"

Each chip arg is "Label=#rrggbb". Text color (black/white) is auto-chosen for
contrast. The Inter font (units-per-em 2816) is downloaded & cached next to this
script on first run (one-time network fetch).

Requires: fonttools   ->  pip install fonttools

IMPORTANT: verify the result by RENDERING it (see preview.js / SKILL.md). Never
judge a badge's size by its `scale` value alone - that is relative to the font's
units-per-em, so the same scale renders different sizes across different fonts.
Generate every badge file in a project from THIS font so they all match.
"""
import os
import sys
import urllib.request

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

# Inter SemiBold, units-per-em 2816. Keep this exact font so every badge matches.
FONT_URL = "https://cdn.jsdelivr.net/npm/@fontsource/inter@5.0.0/files/inter-latin-600-normal.woff"
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inter600.woff")

# House style - keep identical across all badge files so rows line up.
H, F, PADX, GAP, RX = 30, 14, 12, 8, 8


def _load_font():
    if not os.path.exists(FONT_PATH):
        sys.stderr.write("downloading Inter (one-time)...\n")
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    return TTFont(FONT_PATH)


def _text_color(bg):
    """Pick near-black or white text for contrast against the chip color."""
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return "#ffffff" if luminance < 0.6 else "#1b1b1b"


def generate(out_path, chips):
    """chips: list of (label, '#rrggbb'). Writes one centered row of pills as SVG."""
    font = _load_font()
    upem = font["head"].unitsPerEm
    cap = getattr(font["OS/2"], "sCapHeight", int(0.72 * upem)) or int(0.72 * upem)
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    scale = F / upem
    baseline = round((H + cap * scale) / 2)

    def text_path_and_width(s):
        pen = SVGPathPen(glyphs)
        x = 0
        for ch in s:
            name = cmap.get(ord(ch))
            if name is None:                      # missing glyph -> half-em space
                x += int(0.5 * upem)
                continue
            glyphs[name].draw(TransformPen(pen, (1, 0, 0, 1, x, 0)))
            x += glyphs[name].width
        return pen.getCommands(), x * scale

    widths = [text_path_and_width(label)[1] + 2 * PADX for label, _ in chips]
    total = sum(widths) + GAP * (len(chips) - 1)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total:.0f}" '
           f'height="{H}" viewBox="0 0 {total:.0f} {H}" fill="none">']
    x = 0.0
    for (label, bg), w in zip(chips, widths):
        d, _ = text_path_and_width(label)
        fg = _text_color(bg)
        out.append(f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="{H}" rx="{RX}" fill="{bg}"/>')
        out.append(f'<path transform="translate({x + PADX:.2f},{baseline}) '
                   f'scale({scale:.6f},{-scale:.6f})" d="{d}" fill="{fg}"/>')
        x += w + GAP
    out.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("".join(out))
    print(f"wrote {out_path}: {total:.0f}x{H}  font={F}px  cap={cap * scale:.2f}px  upem={upem}")
    print("  -> verify: cap should be ~10.2px and upem 2816 to match the standard pills")
    return out_path


def _parse_chip(arg):
    if "=" not in arg:
        sys.exit(f"bad chip {arg!r} - use \"Label=#rrggbb\"")
    label, color = arg.rsplit("=", 1)
    if not (color.startswith("#") and len(color) == 7):
        sys.exit(f"bad color {color!r} - use #rrggbb")
    return (label, color)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('usage: python make_badges.py OUT.svg "Label=#rrggbb" ["Label2=#rrggbb" ...]')
    generate(sys.argv[1], [_parse_chip(a) for a in sys.argv[2:]])
