#!/usr/bin/env python3
"""Generate the exact personal-site QR, then verify using independent ZXing."""
import hashlib
import importlib.metadata
import json
from pathlib import Path

import qrcode
from PIL import Image
import zxingcpp

OUT = Path(__file__).resolve().parent
PAYLOAD = 'https://futurizerush.github.io/'
QUIET_ZONE = 4
PIXELS_PER_MODULE = 40
PRINT_WIDTH_MM = 65
qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H,
                   box_size=PIXELS_PER_MODULE, border=QUIET_ZONE)
qr.add_data(PAYLOAD, optimize=0)
qr.make(fit=True)
matrix = [[bool(value) for value in row] for row in qr.modules]
side = len(matrix)
total = side + 2 * QUIET_ZONE
module_mm = PRINT_WIDTH_MM / total
assert module_mm > 2 * 25.4 / 72

# Build one path per dark module from the deterministic encoder output. The SVG
# viewBox includes a real four-module quiet zone; no logo or decorative damage.
path = ''.join(f'M{x+QUIET_ZONE},{y+QUIET_ZONE}h1v1h-1z'
               for y, row in enumerate(matrix) for x, value in enumerate(row) if value)
for suffix, background in [('transparent', ''), ('white', f'<rect width="{total}" height="{total}" fill="#ffffff"/>')]:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="65mm" height="65mm" '
           f'viewBox="0 0 {total} {total}" role="img" aria-labelledby="qr-title" '
           f'shape-rendering="crispEdges">\n'
           f'<title id="qr-title">QR code for {PAYLOAD}</title>\n'
           f'{background}\n<path fill="#000000" d="{path}"/>\n</svg>\n')
    (OUT / f'futurizerush-qr-{suffix}.svg').write_text(svg)
image = qr.make_image(fill_color='#000000', back_color='#ffffff').convert('RGB')
image_path = OUT / 'futurizerush-qr-white.png'
image.save(image_path, dpi=(image.width / (PRINT_WIDTH_MM / 25.4),) * 2)
(OUT / 'matrix.json').write_text(json.dumps({
    'payload': PAYLOAD, 'version': qr.version, 'error_correction': 'H',
    'dimension_without_border': side, 'border_included': False,
    'matrix': matrix,
}, indent=2) + '\n')

# Encoder and decoder are independent libraries. Test original plus nearest-
# neighbor and anti-aliased reductions. These are software checks, not fabric tests.
checks = []
for size, resampling in [(image.width, 'original'), (total*20, 'nearest'),
                         (total*10, 'nearest'), (total*5, 'nearest'),
                         (300, 'lanczos'), (196, 'lanczos'), (130, 'lanczos')]:
    if resampling == 'original':
        candidate = Image.open(image_path).convert('RGB')
    else:
        method = Image.Resampling.NEAREST if resampling == 'nearest' else Image.Resampling.LANCZOS
        candidate = image.resize((size, size), method)
    decoded = zxingcpp.read_barcode(candidate)
    assert decoded is not None, f'No decode: {size}/{resampling}'
    assert decoded.text == PAYLOAD, (size, resampling, decoded.text)
    checks.append({'pixels': [size, size], 'resampling': resampling,
                   'decoder': 'zxing-cpp', 'decoded': decoded.text, 'passed': True})

versions = {package: importlib.metadata.version(package) for package in ['qrcode', 'pillow', 'zxing-cpp']}
metadata = {
    'payload': PAYLOAD, 'redirect_service': None, 'tracking': False,
    'encoder': 'python-qrcode', 'error_correction': 'H', 'version': qr.version,
    'matrix_side_modules': side, 'quiet_zone_modules_per_side': QUIET_ZONE,
    'total_side_modules': total, 'png_pixels': [image.width, image.height],
    'png_pixels_per_module': PIXELS_PER_MODULE,
    'print_size_mm_including_quiet_zone': [PRINT_WIDTH_MM, PRINT_WIDTH_MM],
    'module_size_mm_at_print': module_mm,
    'module_size_points_at_print': module_mm * 72 / 25.4,
    'minimum_module_size_mm_requested': 2 * 25.4 / 72,
    'quiet_zone_mm_per_side_at_print': QUIET_ZONE * module_mm,
    'artwork_color': '#000000',
    'transparent_svg_instruction': 'Use on plain white garment; keep the entire four-module border free of other printing.',
    'packages': versions, 'checks': checks,
    'verification_limit': 'Independent software decoder passed; no physical printed-fabric or phone-camera scan test has been performed.',
    'sha256': {name: hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in [
        'futurizerush-qr-transparent.svg', 'futurizerush-qr-white.svg', 'futurizerush-qr-white.png', 'matrix.json']},
}
(OUT / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
(OUT / 'requirements.txt').write_text(''.join(f'{name}=={version}\n' for name,version in versions.items()))
(OUT / 'README.md').write_text(f'''# Futurizerush QR

Exact encoded URL: `{PAYLOAD}` (including the final slash).

- `futurizerush-qr-transparent.svg`: black vector modules and transparent quiet zone, for white T-shirt artwork.
- `futurizerush-qr-white.svg`: black vector modules with a white background, for the website.
- `futurizerush-qr-white.png`: {image.width} × {image.height} pixels, {PIXELS_PER_MODULE} integer pixels per module.
- `matrix.json`: the borderless boolean matrix; `true` means black.
- `metadata.json`: measurements, file hashes, dependency versions, and independent decoder results.

Print the whole QR canvas at **65 × 65 mm**, including its four-module quiet zone.
QR version {qr.version}, error correction H, {side} × {side} data canvas / {total} × {total} including border.
Each module is **{module_mm:.4f} mm = {module_mm * 72 / 25.4:.4f} pt** at that size (above 2 pt).
Each quiet-zone edge is **{QUIET_ZONE * module_mm:.4f} mm**. Preserve a plain white area across that border; do not crop it or add nearby marks inside it.
Do not insert a logo, alter individual modules, stretch the square, or rasterize at a low resolution.

## Reproduce

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python generate_qr.py
```

The independent ZXing decoder verifies the full URL in the original PNG and six resized versions, including anti-aliased reductions. **This is software validation only. It is not a physical print, textile, or phone-camera test.**
''')
print(json.dumps({key:metadata[key] for key in ['payload','version','matrix_side_modules','total_side_modules','png_pixels','module_size_mm_at_print','module_size_points_at_print','checks']}, indent=2))
