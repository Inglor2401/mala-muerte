"""
Mala Muerte — batch image optimizer.
Walks assets/images/, converts each PNG to AVIF + WebP siblings.
Keeps originals untouched. Run from project root:
    python scripts/optimize-images.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pillow_avif  # noqa: F401 — side-effect import registers AVIF encoder
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "assets" / "images"

AVIF_QUALITY = 72   # perceptually lossless around 70-80
WEBP_QUALITY = 82   # WebP needs slightly higher q for same perceived quality

# Hero background can be larger — everything else we cap at 1600px long side
MAX_LONG_SIDE = 2000


def fsize(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0


def fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def optimize_one(src: Path) -> tuple[int, int, int]:
    """Returns (original_bytes, avif_bytes, webp_bytes)."""
    img = Image.open(src).convert("RGB")
    w, h = img.size
    long_side = max(w, h)
    if long_side > MAX_LONG_SIDE:
        scale = MAX_LONG_SIDE / long_side
        img = img.resize(
            (int(w * scale), int(h * scale)),
            Image.Resampling.LANCZOS,
        )

    avif_path = src.with_suffix(".avif")
    webp_path = src.with_suffix(".webp")

    img.save(avif_path, format="AVIF", quality=AVIF_QUALITY, speed=4)
    img.save(webp_path, format="WEBP", quality=WEBP_QUALITY, method=6)

    return fsize(src), fsize(avif_path), fsize(webp_path)


def main() -> None:
    if not IMAGES_DIR.exists():
        print(f"[ERR] Not found: {IMAGES_DIR}", file=sys.stderr)
        sys.exit(1)

    pngs = sorted(IMAGES_DIR.rglob("*.png"))
    if not pngs:
        print("[INFO] No PNG files to optimize.")
        return

    total_orig = 0
    total_avif = 0
    total_webp = 0
    t0 = time.perf_counter()

    print(f"Optimizing {len(pngs)} PNG files…\n")
    print(f"{'File':<42} {'PNG':>10} {'AVIF':>10} {'WebP':>10} {'Saved':>8}")
    print("-" * 84)

    for png in pngs:
        rel = png.relative_to(IMAGES_DIR)
        orig, avif, webp = optimize_one(png)
        total_orig += orig
        total_avif += avif
        total_webp += webp
        saved = 1 - (avif / orig) if orig else 0
        print(
            f"{str(rel):<42} "
            f"{fmt_size(orig):>10} "
            f"{fmt_size(avif):>10} "
            f"{fmt_size(webp):>10} "
            f"{saved*100:>7.0f}%"
        )

    print("-" * 84)
    print(
        f"{'TOTAL':<42} "
        f"{fmt_size(total_orig):>10} "
        f"{fmt_size(total_avif):>10} "
        f"{fmt_size(total_webp):>10} "
        f"{(1-total_avif/total_orig)*100 if total_orig else 0:>7.0f}%"
    )
    print(f"\nDone in {time.perf_counter()-t0:.1f}s.")


if __name__ == "__main__":
    main()
