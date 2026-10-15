"""Build the standalone deck: inline the fonts, the logo, figures, and any data files into one offline HTML file.

Inputs:  src/deck.html, fonts/fonts.css and fonts/*.woff2, assets/ida-logo.png, figures/*, data/<name>.json
Output:  <folder name>.html beside this script
Run:     pixi run --manifest-path ~/.claude/skills/_shared/pixi.toml python build.py
         (stdlib only, so any environment with Python 3.10+ also works)

Markers in src/deck.html:
  /*@FONTS@*/          replaced by the @font-face rules with each woff2 inlined
  url("@LOGO@")        replaced by the logo as a data URI (appears once, in the --logo token)
  /*@DATA:name@*/      replaced by `const NAME = <data/name.json>;` for charts drawn in the page
  src="figures/<file>" replaced by the file as a data URI (png, jpg, gif, svg, webp)
"""

import base64
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src" / "deck.html"
OUT = HERE / f"{HERE.name}.html"


def font_faces() -> str:
    css = (HERE / "fonts" / "fonts.css").read_text()

    def inline(match: re.Match) -> str:
        data = base64.b64encode((HERE / match.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"

    return re.sub(r"url\((fonts/[^)]+)\)", inline, css)


def logo_uri() -> str:
    data = base64.b64encode((HERE / "assets" / "ida-logo.png").read_bytes()).decode()
    return f'url("data:image/png;base64,{data}")'


IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}


def inline_figure(match: re.Match) -> str:
    path = HERE / match.group(1)
    assert path.exists(), f"{match.group(1)} is cited in src/deck.html but not found"
    mime = IMAGE_TYPES.get(path.suffix.lower())
    assert mime, f"{match.group(1)}: unsupported image type {path.suffix}"
    data = base64.b64encode(path.read_bytes()).decode()
    return f'src="data:{mime};base64,{data}"'


def inline_data(match: re.Match) -> str:
    name = match.group(1)
    payload = json.loads((HERE / "data" / f"{name}.json").read_text())
    return f"const {name.upper()} = {json.dumps(payload)};"


def main() -> None:
    html = SRC.read_text()
    assert html.count("/*@FONTS@*/") == 1, f"expected one /*@FONTS@*/ marker in {SRC}"
    html = html.replace("/*@FONTS@*/", font_faces())
    if 'url("@LOGO@")' in html:
        html = html.replace('url("@LOGO@")', logo_uri())
    html, n_figures = re.subn(r'src="(figures/[^"]+)"', inline_figure, html)
    html, n_data = re.subn(r"/\*@DATA:([A-Za-z_][A-Za-z0-9_]*)@\*/", inline_data, html)
    leftover = re.findall(r"/\*@[A-Z]+[^*]*@\*/|@LOGO@", html)
    assert not leftover, f"unreplaced markers: {leftover}"
    OUT.write_text(html)
    n_slides = len(re.findall(r'<section class="slide[" ]', html))
    print(f"wrote {OUT.name} ({OUT.stat().st_size / 1024:.0f} KB), {n_slides} slides, {n_figures} figures, {n_data} data blocks")


if __name__ == "__main__":
    main()
