# Profile badge tools

The tech-stack "pills" in the profile README (`assets/tags-*.svg`) are generated as
self-contained SVGs with the **Inter** font outlined to vector paths. Outlining means
the glyphs are baked-in `<path>` geometry, so the chips render identically in every
browser and through GitHub's image proxy — no font to load, no shields.io Verdana.

## Regenerate a pill row

```bash
# needs: pip install fonttools   (Inter is auto-downloaded & cached on first run)
python tools/make_badges.py assets/tags-myproject.svg \
  "C=#555555" "Winsock2=#0078D4" "Win32 Threads=#2EA44F" "TCP Sockets=#E81F26"
```

Each arg is `Label=#rrggbb`. Text color (black/white) is auto-chosen for contrast.
House style (height 30, font 14px, padding 12, gap 8, radius 8) lives at the top of
`make_badges.py` — change it there to restyle every pill consistently.

## ⚠️ Keep every pill the same font

A pill's visual text size is `cap-height × scale`, **not** the `scale` value alone —
that scale is relative to the font's units-per-em (UPEM). This Inter is **UPEM 2816**;
a different Inter/font at the same scale renders a different size (this caused a pill
that looked ~26% too small once). `make_badges.py` prints `cap≈10.18px upem=2816` —
if that matches, the new pill lines up with the others. Always regenerate from this
script so they stay uniform.

## Verify before shipping

Don't trust the SVG source — render it and look:

```bash
npm i @resvg/resvg-js
node tools/preview.js assets/tags-myproject.svg out.png 4   # then open out.png
```

Render the new pill and an existing good one at the same zoom; the capital letters
should be the same height.

## Deploying (cache-busting)

GitHub's image proxy caches by URL for a long time. If you change a pill's content,
the surest way to make the new version show is to **rename the file to a new path**
and update the README reference — a path the proxy has never seen can't be stale.
(`?v=N` query bumps sometimes work but can get stuck.) After pushing, confirm the live
profile page references the new filename:

```bash
curl -sS -A "Mozilla/5.0" https://github.com/judelahage | grep -c 'tags-myproject'
```
