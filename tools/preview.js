// preview.js - rasterize an SVG to PNG so you can SEE it.
//
// Visual bugs (especially the units-per-em font-size trap) hide in SVG source.
// Render and look instead of reasoning from the markup. To check sizing, render
// the new badge AND a known-good one at the SAME zoom, then compare the height of
// the capital letters.
//
// Setup (once, in a scratch dir):  npm i @resvg/resvg-js
// Usage:                           node preview.js in.svg [out.png] [zoom]
//   in.svg   path to the SVG to render
//   out.png  output path (default: preview.png)
//   zoom     integer scale factor (default: 4)
//
// Windows/git-bash note: Node resolves "/tmp/x" as "C:\tmp\x", while git-bash
// "/tmp" is "%LOCALAPPDATA%\Temp". Use paths relative to your cwd or full Windows
// paths when bridging the two.

const { Resvg } = require("@resvg/resvg-js");
const fs = require("fs");

const inPath = process.argv[2];
const outPath = process.argv[3] || "preview.png";
const zoom = Number(process.argv[4] || 4);

if (!inPath) {
  console.error('usage: node preview.js in.svg [out.png] [zoom]');
  process.exit(1);
}

const resvg = new Resvg(fs.readFileSync(inPath), {
  background: "white", // so colored chips with white text are visible in the PNG
  fitTo: { mode: "zoom", value: zoom },
});
const png = resvg.render();
fs.writeFileSync(outPath, png.asPng());
console.log(`rendered ${inPath} -> ${outPath} (${png.width}x${png.height}, zoom ${zoom}x)`);
