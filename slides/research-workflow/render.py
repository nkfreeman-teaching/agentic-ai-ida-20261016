"""Render every slide (all builds shown) to PNG, check the layout, collect console errors, and export the PDF.

Run:  pixi run --manifest-path ~/.claude/skills/_shared/pixi.toml python render.py OUTDIR [--theme light|dark|both] [--pdf]

Each slide is loaded fresh at its own hash so it renders from a clean state. The layout check flags
(i) any visible element that extends past the 1920x1080 slide, and (ii) any element whose text is
clipped by its own box (content taller or wider than an element with overflow hidden). A clean
check does not replace looking at the PNGs; it catches the failures that are easy to miss by eye.
Exit code is 1 when the check or the console reports a problem, so a caller can gate on it.
"""

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DECK = HERE / f"{HERE.name}.html"
CHROME = "/usr/bin/google-chrome"

LAYOUT_CHECK = """
(slide) => {
  const box = slide.getBoundingClientRect();
  const problems = [];
  const label = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '') +
    ' "' + (el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 50) + '"';
  for (const el of slide.querySelectorAll('*')) {
    if (el.closest('aside.notes, defs, marker')) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const tol = 2;
    if (r.left < box.left - tol || r.top < box.top - tol || r.right > box.right + tol || r.bottom > box.bottom + tol) {
      problems.push('outside slide: ' + label(el));
    }
    const clips = ['hidden', 'clip'].includes(cs.overflowX) || ['hidden', 'clip'].includes(cs.overflowY);
    if (clips && !(el instanceof SVGElement) && (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2)) {
      problems.push('clipped content: ' + label(el));
    }
  }
  return problems;
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render deck slides to PNG and export the PDF.")
    parser.add_argument("outdir", type=Path, help="Directory for slide PNGs (one subfolder per theme).")
    parser.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    parser.add_argument("--pdf", action="store_true", help="Also export the light-theme PDF beside the deck.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not DECK.exists():
        sys.exit(f"{DECK.name} not found; run build.py first")
    themes = ["light", "dark"] if args.theme == "both" else [args.theme]
    errors: list[str] = []
    layout: list[str] = []
    with sync_playwright() as p:
        launch = {"executable_path": CHROME} if Path(CHROME).exists() else {}
        browser = p.chromium.launch(**launch)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(DECK.as_uri() + "?all#1")
        page.wait_for_timeout(800)
        n = page.evaluate("document.querySelectorAll('section.slide').length")
        for theme in themes:
            out = args.outdir / theme
            out.mkdir(parents=True, exist_ok=True)
            for i in range(1, n + 1):
                page.goto(DECK.as_uri() + f"?all#{i}.99")
                page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
                page.wait_for_timeout(900)
                page.screenshot(path=str(out / f"slide-{i:02d}.png"))
                if theme == themes[0]:
                    slide = page.locator("section.slide.active")
                    layout += [f"slide {i}: {msg}" for msg in slide.evaluate(LAYOUT_CHECK)]
        if args.pdf:
            page.goto(DECK.as_uri() + "?all#1")
            page.evaluate("document.documentElement.dataset.theme = 'light'")
            page.wait_for_timeout(800)
            page.emulate_media(media="print")
            pdf = DECK.with_suffix(".pdf")
            page.pdf(path=str(pdf), width="1920px", height="1080px", print_background=True)
            print(f"wrote {pdf.name}")
        browser.close()
    print(f"slides={n} themes={','.join(themes)} console_errors={len(errors)} layout_flags={len(layout)}")
    for e in errors:
        print("CONSOLE:", e)
    for msg in layout:
        print("LAYOUT:", msg)
    return 1 if errors or layout else 0


if __name__ == "__main__":
    sys.exit(main())
