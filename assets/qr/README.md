# Futurizerush QR

Exact encoded URL: `https://futurizerush.github.io/` (including the final slash).

- `futurizerush-qr-transparent.svg`: black vector modules and transparent quiet zone, for white T-shirt artwork.
- `futurizerush-qr-white.svg`: black vector modules with a white background, for the website.
- `futurizerush-qr-white.png`: 1640 × 1640 pixels, 40 integer pixels per module.
- `matrix.json`: the borderless boolean matrix; `true` means black.
- `metadata.json`: measurements, file hashes, dependency versions, and independent decoder results.

Print the whole QR canvas at **65 × 65 mm**, including its four-module quiet zone.
QR version 4, error correction H, 33 × 33 data canvas / 41 × 41 including border.
Each module is **1.5854 mm = 4.4940 pt** at that size (above 2 pt).
Each quiet-zone edge is **6.3415 mm**. Preserve a plain white area across that border; do not crop it or add nearby marks inside it.
Do not insert a logo, alter individual modules, stretch the square, or rasterize at a low resolution.

## Reproduce

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python generate_qr.py
```

The independent ZXing decoder verifies the full URL in the original PNG and six resized versions, including anti-aliased reductions. **This is software validation only. It is not a physical print, textile, or phone-camera test.**
