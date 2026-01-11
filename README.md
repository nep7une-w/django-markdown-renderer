# Django Markdown Renderer

A minimal Django app that lets users compose Markdown with live preview, MathJax math rendering, and one-click export to `.md` or `.pdf`.

## Features

- Live Markdown editor with server-rendered preview
- Math equation rendering via MathJax (`$...$` and `$$...$$`)
- Export Markdown as `.md`
- Export rendered HTML as `.pdf` (server-side)

## Tech Stack

- Django 4.x
- Python-Markdown with `pymdown-extensions` (`arithmatex`)
- MathJax 3 for client-side math rendering
- xhtml2pdf for PDF export

## Project Structure

- `manage.py` Django entry point
- `mdrenderer/` Django project settings and URLs
- `editor/` App views and configuration
- `templates/editor.html` UI and client-side logic
- `requirements.txt` Python dependencies

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Usage

- Type Markdown in the left panel; the right panel updates automatically.
- Use `$...$` for inline math and `$$...$$` for block math.
- Export buttons download `document.md` or `document.pdf`.

## Notes

- PDF export uses xhtml2pdf, which supports a limited subset of CSS. Keep styles simple.
- Math rendering in the PDF export is not handled by MathJax; the PDF is generated from server-side HTML.
