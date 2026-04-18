# Mala Muerte

Портфолио-проект: премиум сайт мексиканского бара в стиле Día de los Muertos.

## Стек

- Vanilla HTML / CSS / JS (без билд-шага)
- Cascade layers CSS, fluid typography, CSS Grid + Container queries
- Lenis (smooth scroll) + GSAP ScrollTrigger через CDN
- Изображения: AVIF / WebP / PNG через `<picture>` — 94% экономия против PNG
- Hero-видео: 8-сек loop, MP4 H.264, `prefers-reduced-motion` fallback

## Структура

```
mala-muerte/
├── index.html          Главная
├── menu.html           Меню (8 коктейлей + 4 блюда)
├── team.html           Команда (7 карт + групповое)
├── reservation.html    Форма резервации
├── contacts.html       Контакты
├── assets/
│   ├── css/            tokens, base, components, pages/*
│   ├── js/             main.js
│   ├── images/         team/ + interior/ + menu/ (avif/webp/png)
│   ├── video/          hero-loop.mp4
│   └── svg/            орнаменты + плейсхолдеры
├── scripts/
│   ├── optimize-images.py    PNG → AVIF + WebP batch
│   └── html-to-picture.py    <img> → <picture> wrapper
└── vercel.json         Cache headers + security headers
```

## Локально

```bash
python -m http.server 5174
# или — см. .claude/launch.json в родительской папке
```

Открыть `http://localhost:5174/`.

## Деплой

Автодеплой через Vercel при push в main:

```bash
git push
```

## A11y

- Skip-link на каждой странице
- Все изображения с `alt`
- Семантические landmarks: `main#main`, `nav`, `footer`
- Форма резервации: все контролы с `<label for>`
- Модалка: Escape + backdrop-click + focus trap + focus return
- `prefers-reduced-motion` отключает hero-видео
- Контраст текста 11:1 (WCAG AAA)
- Адаптив 360 / 768 / 1280 / 1920 — без горизонтального скролла
