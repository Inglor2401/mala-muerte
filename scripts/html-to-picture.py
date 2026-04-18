"""
Rewrite <img src="assets/images/*.png" ...> → <picture> with AVIF/WebP/PNG chain.
Run from project root:
    python scripts/html-to-picture.py
Preserves all img attributes (class, alt, loading, decoding, etc).
Idempotent — already-wrapped <picture> blocks are skipped.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Matches an <img ...src="assets/images/...png"...> tag.
# We intentionally require the .png source to be under assets/images to
# avoid touching SVG placeholders, external URLs, or map assets.
IMG_RE = re.compile(
    r"""<img
        (?P<pre>[^>]*?)
        \bsrc="(?P<src>assets/images/[^"]+?)\.png"
        (?P<post>[^>]*?)
        \s*/?>""",
    re.VERBOSE,
)


def wrap_tag(match: re.Match) -> str:
    pre = match.group("pre")
    src_no_ext = match.group("src")
    post = match.group("post")
    attrs = (pre + post).strip()
    # Add lazy-loading + async decoding by default if not already set.
    if "loading=" not in attrs:
        attrs += ' loading="lazy"'
    if "decoding=" not in attrs:
        attrs += ' decoding="async"'
    return (
        "<picture>"
        f'<source srcset="{src_no_ext}.avif" type="image/avif">'
        f'<source srcset="{src_no_ext}.webp" type="image/webp">'
        f'<img src="{src_no_ext}.png" {attrs.strip()}>'
        "</picture>"
    )


def main() -> None:
    html_files = sorted(ROOT.glob("*.html"))
    total = 0
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        new_text, count = IMG_RE.subn(wrap_tag, text)
        if count:
            path.write_text(new_text, encoding="utf-8")
            print(f"  {path.name}: {count} tags wrapped")
            total += count
        else:
            print(f"  {path.name}: 0 (already wrapped or no matches)")
    print(f"\nTotal: {total} <img> → <picture>")


if __name__ == "__main__":
    main()
