// News-image entry for make.fun's "Sum up 19 November's world news in one image"
// bounty (news-image-20261118). Node 22, standard library only.
//
// The program runs in a sandbox with no network and a read-only /bot, so the
// finished front page is committed beside this file as entry.png (a JPEG's
// bytes under a .png name, which the gate accepts: it tells PNG from JPEG by
// the first bytes). All this program does is copy it to the output path.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// After copying, the program verifies the output before exiting: a corrupt,
// truncated or oversized copy used to be passed on silently and only fail at
// the gate, so it now checks the copy is byte-identical to the committed
// image, within the gate's 1 MiB cap, and a whole PNG/JPEG no larger than
// 1024x1024 — and exits non-zero with a clear error if any check fails.

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const MAX_BYTES = 1048576;
const MAX_DIM = 1024;

// Dimensions from the image header: PNG IHDR, or the first JPEG SOF marker.
function dimensions(buf: Buffer): { width: number; height: number } {
  if (
    buf.length >= 24 &&
    buf.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))
  ) {
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  }
  if (buf.length >= 2 && buf[0] === 0xff && buf[1] === 0xd8) {
    let i = 2;
    while (i + 9 < buf.length) {
      if (buf[i] !== 0xff) throw new Error('entry.png: malformed JPEG marker');
      const marker = buf[i + 1];
      const len = buf.readUInt16BE(i + 2);
      if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
        return { height: buf.readUInt16BE(i + 5), width: buf.readUInt16BE(i + 7) };
      }
      i += 2 + len;
    }
    throw new Error('entry.png: no JPEG SOF marker found (truncated file?)');
  }
  throw new Error('entry.png: not a PNG or JPEG (unrecognised magic bytes)');
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, 'entry.png');
const srcPath = new URL('./entry.png', import.meta.url);
copyFileSync(srcPath, outPath);

const src = readFileSync(srcPath);
const out = readFileSync(outPath);
if (!src.equals(out)) throw new Error('entry.png: copied output differs from the committed image');
if (out.length > MAX_BYTES) {
  throw new Error(`entry.png: ${out.length} bytes exceeds the 1 MiB gate limit`);
}
const { width, height } = dimensions(out);
if (width > MAX_DIM || height > MAX_DIM) {
  throw new Error(`entry.png: ${width}x${height} exceeds the 1024x1024 gate limit`);
}
// Whole image: a JPEG must end with its EOI marker, a PNG with its IEND
// chunk. Headers sit at the front, so dimension checks alone would pass a
// file cut short mid-scan.
const isPng = out[0] === 0x89;
const whole = isPng
  ? out.subarray(out.length - 12).equals(
      Buffer.from([0, 0, 0, 0, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82]),
    )
  : out[out.length - 2] === 0xff && out[out.length - 1] === 0xd9;
if (!whole) throw new Error('entry.png: truncated image data (missing end marker)');
console.log(`wrote ${outPath} (${out.length} bytes, ${width}x${height})`);
