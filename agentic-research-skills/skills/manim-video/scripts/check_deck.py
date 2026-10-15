"""Check that a manim-slides HTML deck plays offline.

Run:
    python check_deck.py DECK.html [--expect N] [--shots DIR]

Two passes, and the exit code is 1 if either finds a defect:
  1. Static. Outside HTML comments, every script, stylesheet, and background video must be a
     local file that exists; any http(s) reference is a defect, since --offline was skipped.
  2. Browser. The installed Chrome opens the page with every non-file request blocked and
     recorded. It checks that reveal.js starts, the slide count matches the sections (and
     --expect, the sum of the parts' breaks), every slide's video decodes, the right arrow
     advances one slide, and typing G, a slide number, and Enter jumps to that slide.
Both passes also check the animation timer (template/shared/clip_timer.js): the page must
load it, and it must show its check once the first slide's clip ends.
--shots saves a PNG of the first slide and the jump target, each taken after its clip ends,
for reading back as images.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Set CHROME_PATH to the Chrome or Chromium executable on your machine.
CHROME = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")
COMMENT = re.compile(r"<!--.*?-->", re.S)
REFERENCE = re.compile(r'<(?:script|link)[^>]*?(?:src|href)="([^"]+)"|data-background-video="([^"]+)"')


def static_check(page):
    html = COMMENT.sub("", page.read_text())
    defects = []
    references = [first or second for first, second in REFERENCE.findall(html)]
    for ref in references:
        if re.match(r"https?:", ref):
            defects.append(f"remote reference {ref}")
        elif not (page.parent / ref).exists():
            defects.append(f"missing file {ref}")
    if not any(ref.endswith("/clip_timer.js") for ref in references):
        defects.append(
            "no animation timer; run shared/add_clip_timer.py on the deck (a project set up "
            "before Oct 14, 2026 copies it and clip_timer.js from the skill's template/shared/)"
        )
    sections = len(re.findall(r"<section\b", html))
    videos = sum(1 for _, second in REFERENCE.findall(html) if second)
    print(f"Static: {len(references)} local references, {sections} sections, {videos} background videos.")
    return defects, sections


def video_ready(page, index, timeout_ms=8000):
    """Wait until slide index's background video has decoded a frame."""
    try:
        page.wait_for_function(
            """(i) => {
                const bg = Reveal.getSlideBackground(i);
                const v = bg && bg.querySelector('video');
                return v && v.readyState >= 2 && v.videoWidth > 0;
            }""",
            arg=index,
            timeout=timeout_ms,
        )
        return True
    except Exception:
        return False


def settle(page, index, timeout_ms=60000):
    """Wait for slide index's clip to finish, so a screenshot shows the settled frame."""
    page.wait_for_function(
        "(i) => { const v = Reveal.getSlideBackground(i).querySelector('video'); return v && v.ended; }",
        arg=index,
        timeout=timeout_ms,
    )
    # The timer's check fades in over 0.25 s after the clip ends.
    page.wait_for_timeout(400)


def timer_state(page):
    return page.evaluate("() => { const t = document.getElementById('clip-timer'); return t ? t.dataset.state : null; }")


def browser_check(page_path, sections, expect, shots):
    defects = []
    blocked = []
    with sync_playwright() as p:
        launch = {"executable_path": CHROME} if Path(CHROME).exists() else {}
        browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"], **launch)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        def route(r):
            if r.request.url.startswith("file:"):
                r.continue_()
            else:
                blocked.append(r.request.url)
                r.abort()

        page.route("**/*", route)
        page.goto(page_path.resolve().as_uri())
        page.wait_for_function("() => window.Reveal && Reveal.isReady()", timeout=15000)

        total = page.evaluate("Reveal.getTotalSlides()")
        print(f"Browser: reveal.js ready with {total} slides.")
        if total != sections:
            defects.append(f"reveal.js reports {total} slides but the page has {sections} sections")
        if expect is not None and total != expect:
            defects.append(f"{total} slides, expected {expect}")

        undecoded = []
        for index in range(total):
            page.evaluate(f"Reveal.slide({index})")
            if not video_ready(page, index):
                undecoded.append(index + 1)
        if undecoded:
            defects.append(f"videos that did not decode on slides {undecoded}")
        print(f"Browser: {total - len(undecoded)} of {total} slide videos decoded.")

        page.evaluate("Reveal.slide(0)")
        settle(page, 0)
        timer = timer_state(page)
        if timer is None:
            defects.append("the animation timer is not on the page")
        elif timer != "done":
            defects.append(f"after slide 1's clip ended the animation timer showed {timer!r}, not 'done'")
        print(f"Browser: after slide 1's clip ended the animation timer showed {timer or 'nothing'}.")
        if shots:
            shots.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(shots / "slide-01.png"))
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(300)
        after_arrow = page.evaluate("Reveal.getIndices().h")
        if after_arrow != 1:
            defects.append(f"right arrow moved to slide {after_arrow + 1}, not 2")

        target = max(1, min(total, (total * 2) // 3))
        page.keyboard.press("g")
        page.keyboard.type(str(target))
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        after_jump = page.evaluate("Reveal.getIndices().h") + 1
        if after_jump != target:
            defects.append(f"G {target} Enter landed on slide {after_jump}")
        print(f"Browser: right arrow went to slide {after_arrow + 1}; G {target} Enter went to slide {after_jump}.")
        if shots:
            settle(page, target - 1)
            page.screenshot(path=str(shots / f"slide-{target:02d}.png"))
        browser.close()
    if blocked:
        defects.append(f"{len(blocked)} network requests blocked, e.g., {blocked[0]}")
    defects.extend(f"page error: {error}" for error in errors)
    return defects


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("deck", type=Path)
    parser.add_argument("--expect", type=int, help="Expected slide count.")
    parser.add_argument("--shots", type=Path, help="Folder for two PNG screenshots.")
    args = parser.parse_args()
    defects, sections = static_check(args.deck)
    defects += browser_check(args.deck, sections, args.expect, args.shots)
    for defect in defects:
        print(f"DEFECT: {defect}")
    print("Deck plays offline." if not defects else f"{len(defects)} defects.")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
