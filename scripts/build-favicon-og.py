"""
Build favicon PNGs (32, 180, 192, 512) + OG image (1200x630) from existing assets.
Run from project root:
    python scripts/build-favicon-og.py
"""
from __future__ import annotations

from pathlib import Path
from io import BytesIO

import pillow_avif  # noqa: F401
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FAVICON_DIR = ROOT / "assets" / "favicon"
OG_DIR = ROOT / "assets" / "og"
GROUP_SHOT = ROOT / "assets" / "images" / "team" / "group-shot.png"

FAVICON_DIR.mkdir(parents=True, exist_ok=True)
OG_DIR.mkdir(parents=True, exist_ok=True)

# ── Brand tokens (match CSS) ──────────────────────────────────────
INK = (11, 13, 20)
INK_SOFT = (20, 24, 38)
BONE = (245, 236, 217)
GOLD = (201, 169, 97)
GOLD_HI = (230, 200, 120)
MARIGOLD = (232, 106, 28)


def _find_font(weight: str = "regular") -> Path | None:
    """Try to find a reasonable Windows font."""
    candidates = {
        "serif-italic": [
            "C:/Windows/Fonts/georgiai.ttf",
            "C:/Windows/Fonts/timesi.ttf",
        ],
        "serif": [
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/times.ttf",
        ],
        "sans": [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ],
    }
    for p in candidates.get(weight, []):
        if Path(p).exists():
            return Path(p)
    return None


def build_favicon_pngs() -> None:
    """Render favicon.svg > PNG at multiple sizes.
    Pillow can't render SVG natively, so we do a plain PIL rendition
    mimicking the SVG: rounded rect + marigold petals + skull.
    """
    for size in (32, 180, 192, 512):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        s = size

        # Rounded rect background
        r = s * 0.19
        d.rounded_rectangle([(0, 0), (s, s)], radius=int(r), fill=INK)
        # Inner soft gradient simulation (two rects with alpha)
        overlay = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([(0, 0), (s, s)], radius=int(r),
                             fill=(14, 42, 51, 110))
        img = Image.alpha_composite(img, overlay)
        d = ImageDraw.Draw(img)

        # Marigold petal row (top)
        petal_y = s * 0.16
        for cx_frac, rx_f, ry_f, rot in [
            (0.5, 0.09, 0.055, 0),
            (0.37, 0.08, 0.05, -25),
            (0.63, 0.08, 0.05, 25),
            (0.27, 0.07, 0.045, -45),
            (0.73, 0.07, 0.045, 45),
        ]:
            cx = s * cx_frac
            petal = Image.new("RGBA", (s, s), (0, 0, 0, 0))
            pd = ImageDraw.Draw(petal)
            pd.ellipse(
                [cx - s * rx_f, petal_y - s * ry_f,
                 cx + s * rx_f, petal_y + s * ry_f],
                fill=MARIGOLD + (230,),
            )
            if rot:
                petal = petal.rotate(rot, center=(cx, petal_y),
                                     resample=Image.Resampling.BICUBIC)
            img = Image.alpha_composite(img, petal)
        d = ImageDraw.Draw(img)

        # Skull body (rounded trapezoid-like using ellipse + rect)
        sk_w = s * 0.56
        sk_h = s * 0.62
        sk_cx = s * 0.5
        sk_cy = s * 0.56
        # Main skull ellipse
        d.ellipse(
            [sk_cx - sk_w/2, sk_cy - sk_h/2,
             sk_cx + sk_w/2, sk_cy + sk_h/2],
            fill=BONE,
        )
        # Jaw extension (rect softened)
        jaw_w = sk_w * 0.7
        d.rounded_rectangle(
            [sk_cx - jaw_w/2, sk_cy + sk_h * 0.10,
             sk_cx + jaw_w/2, sk_cy + sk_h * 0.42],
            radius=int(s * 0.06),
            fill=BONE,
        )

        # Eye sockets
        eye_r = s * 0.08
        eye_y = sk_cy - s * 0.05
        for ex in (sk_cx - s * 0.11, sk_cx + s * 0.11):
            d.ellipse([ex - eye_r, eye_y - eye_r,
                       ex + eye_r, eye_y + eye_r],
                      fill=INK)
            # Gold filigree ring around
            d.ellipse([ex - eye_r - s*0.013, eye_y - eye_r - s*0.013,
                       ex + eye_r + s*0.013, eye_y + eye_r + s*0.013],
                      outline=GOLD, width=max(1, int(s*0.006)))

        # Nose (small triangle)
        nose_y = sk_cy + s * 0.08
        d.polygon([
            (sk_cx - s * 0.03, nose_y),
            (sk_cx + s * 0.03, nose_y),
            (sk_cx, nose_y + s * 0.05),
        ], fill=INK)

        # Smile line
        smile_y = sk_cy + s * 0.21
        smile_hw = s * 0.14
        d.line([(sk_cx - smile_hw, smile_y),
                (sk_cx + smile_hw, smile_y)],
               fill=INK, width=max(1, int(s*0.018)))
        # Stitches across smile
        for i in range(-3, 4):
            tx = sk_cx + i * s * 0.04
            d.line([(tx, smile_y - s*0.022),
                    (tx, smile_y + s*0.022)],
                   fill=INK, width=max(1, int(s*0.014)))

        out = FAVICON_DIR / f"favicon-{size}.png"
        img.save(out, format="PNG", optimize=True)
        print(f"  favicon-{size}.png  ({out.stat().st_size/1024:.1f} KB)")

    # apple-touch-icon (180 exists, copy as canonical)
    apple = FAVICON_DIR / "apple-touch-icon.png"
    (FAVICON_DIR / "favicon-180.png").replace(apple)
    print(f"  apple-touch-icon.png (renamed from 180)")


def build_og_image() -> None:
    """1200×630 OG image: group shot cropped + dark gradient overlay + title."""
    if not GROUP_SHOT.exists():
        print(f"[WARN] group-shot not found at {GROUP_SHOT}")
        return

    og = Image.open(GROUP_SHOT).convert("RGB")
    # Crop to 1200×630 ratio (~1.905). Group shot is ~2.357 (21:9).
    target_ratio = 1200 / 630
    w, h = og.size
    src_ratio = w / h
    if src_ratio > target_ratio:
        # Crop sides
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        og = og.crop((left, 0, left + new_w, h))
    else:
        # Crop top/bottom
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        og = og.crop((0, top, w, top + new_h))
    og = og.resize((1200, 630), Image.Resampling.LANCZOS)

    # Dark overlay gradient bottom
    overlay = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(630):
        alpha = int(220 * (y / 630) ** 1.6)
        od.rectangle([0, y, 1200, y+1], fill=(11, 13, 20, alpha))
    og = Image.alpha_composite(og.convert("RGBA"), overlay).convert("RGB")

    # Title text
    d = ImageDraw.Draw(og)
    serif_italic = _find_font("serif-italic")
    sans = _find_font("sans")

    if serif_italic:
        title_font = ImageFont.truetype(str(serif_italic), size=108)
        d.text((72, 420), "Mala", font=title_font, fill=BONE)
        d.text((72, 520), "Muerte", font=title_font, fill=MARIGOLD)
    else:
        # Fallback: default font
        d.text((72, 460), "Mala Muerte", fill=BONE)

    if sans:
        sub_font = ImageFont.truetype(str(sans), size=26)
        d.text(
            (72, 380),
            "Авторский мескаль-бар · Día de los Muertos",
            font=sub_font, fill=GOLD,
        )
        # URL bottom right
        url_font = ImageFont.truetype(str(sans), size=22)
        d.text(
            (900, 575), "inglor2401.github.io",
            font=url_font, fill=GOLD,
        )

    # Gold hairline top-left
    d.line([(72, 370), (72 + 120, 370)], fill=GOLD, width=2)

    out = OG_DIR / "og-image.jpg"
    og.save(out, format="JPEG", quality=88, optimize=True)
    print(f"  og-image.jpg  ({out.stat().st_size/1024:.1f} KB, 1200x630)")

    # Also save a smaller Twitter summary version (same aspect works)
    # Twitter accepts 1200×630 for summary_large_image — same file works.


def main() -> None:
    print("> Favicons")
    build_favicon_pngs()
    print("\n> OG image")
    build_og_image()
    print("\nDone.")


if __name__ == "__main__":
    main()
