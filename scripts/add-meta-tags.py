"""
Inject favicon + OpenGraph + Twitter Card + canonical meta tags into
all 5 HTML pages. Idempotent — wrapped in a marker comment so re-runs
just replace the block.
Run from project root:
    python scripts/add-meta-tags.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://inglor2401.github.io/mala-muerte"
OG_IMAGE = f"{BASE_URL}/assets/og/og-image.jpg"

MARKER_START = "<!-- BEGIN AUTO META -->"
MARKER_END = "<!-- END AUTO META -->"

# Per-page OG/Twitter data
PAGES = {
    "index.html": {
        "slug": "",
        "title": "Mala Muerte · Авторский мескаль-бар",
        "desc": "Mala Muerte — авторские мескаль-коктейли, аутентичная кухня и атмосфера Día de los Muertos. Резервация онлайн.",
    },
    "menu.html": {
        "slug": "menu.html",
        "title": "Меню · Mala Muerte",
        "desc": "Карта авторских мескаль-коктейлей и аутентичная мексиканская кухня. Оахака, Пуэбла, Юкатан.",
    },
    "team.html": {
        "slug": "team.html",
        "title": "Команда · Mala Muerte",
        "desc": "Семеро, которые встретят вас каждый вечер. Хостес, бармены, официанты — семья Mala Muerte.",
    },
    "reservation.html": {
        "slug": "reservation.html",
        "title": "Резервация · Mala Muerte",
        "desc": "Забронируйте столик в Mala Muerte онлайн. Пятница и суббота — бронь обязательна.",
    },
    "contacts.html": {
        "slug": "contacts.html",
        "title": "Контакты · Mala Muerte",
        "desc": "Адрес, часы работы, телефон и соцсети Mala Muerte.",
    },
}


def build_block(page: dict) -> str:
    url = f"{BASE_URL}/{page['slug']}" if page["slug"] else BASE_URL + "/"
    title_html = page["title"].replace('"', '&quot;')
    desc_html = page["desc"].replace('"', '&quot;')
    return f"""  {MARKER_START}
  <link rel="icon" type="image/svg+xml" href="assets/favicon/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon/favicon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="assets/favicon/favicon-192.png">
  <link rel="icon" type="image/png" sizes="512x512" href="assets/favicon/favicon-512.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/favicon/apple-touch-icon.png">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Mala Muerte">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{title_html}">
  <meta property="og:description" content="{desc_html}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Team of Mala Muerte - seven people in Dia de los Muertos makeup">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title_html}">
  <meta name="twitter:description" content="{desc_html}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  {MARKER_END}"""


def inject(text: str, block: str) -> str:
    # If marker block already exists — replace it
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(block.strip(), text)
    # Otherwise inject right before </head>
    return text.replace("</head>", block + "\n</head>", 1)


def main() -> None:
    for name, data in PAGES.items():
        path = ROOT / name
        if not path.exists():
            print(f"  [skip] {name} not found")
            continue
        original = path.read_text(encoding="utf-8")
        new = inject(original, build_block(data))
        if new != original:
            path.write_text(new, encoding="utf-8")
            print(f"  [ok] {name}: meta block injected/updated")
        else:
            print(f"  [=] {name}: no change")


if __name__ == "__main__":
    main()
