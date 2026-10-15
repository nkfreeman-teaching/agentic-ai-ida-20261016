# Copied from <skills>/manim-video/template on __DATE__.
"""Add the animation timer (clip_timer.js) to a manim-slides HTML deck.

Run:
    pixi run python shared/add_clip_timer.py <video>/output/deck/<Name>.html

render.sh calls this after every deck build. It copies clip_timer.js into the deck's assets
folder and loads it at the end of the page, after reveal.js has started. Running it twice
leaves one copy of the script tag, so it can also update a deck built earlier without
re-rendering any video.
"""

import shutil
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("clip_timer.js")

deck = Path(sys.argv[1])
assets = deck.with_name(f"{deck.stem}_assets")
if not assets.is_dir():
    raise SystemExit(f"{assets} is missing; is {deck} a manim-slides deck?")
shutil.copyfile(SCRIPT, assets / SCRIPT.name)

tag = f'<script src="{assets.name}/{SCRIPT.name}"></script>'
html = deck.read_text()
if tag in html:
    print(f"{deck} already loads the animation timer; refreshed {SCRIPT.name}.")
else:
    if html.count("</body>") != 1:
        raise SystemExit(f"{deck} should have exactly one </body> tag.")
    deck.write_text(html.replace("</body>", f"{tag}\n</body>"))
    print(f"Animation timer added to {deck}.")
