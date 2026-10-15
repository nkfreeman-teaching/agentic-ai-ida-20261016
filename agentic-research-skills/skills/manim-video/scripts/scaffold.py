"""Copy the manim-video template into a project and add one video folder.

Run from the project root:
    python scaffold.py SLUG --title "Title" [--dest manim]

The first run copies template/ (minus video-skeleton/) to DEST, which defaults to manim/.
Every run then adds DEST/SLUG/ with a scene module, video.conf, and README from
video-skeleton/. Template files carry __DATE__, __PROJECT__, and video tokens, which are
filled here. It never overwrites: an existing DEST keeps its shared code (a project keeps
the copy its videos were built with), and an existing DEST/SLUG stops the script.
"""

import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "template"
SKELETON = "video-skeleton"


def fill(path, tokens):
    text = path.read_text()
    for token, value in tokens.items():
        text = text.replace(token, value)
    path.write_text(text)


def main():
    parser = argparse.ArgumentParser(description="Scaffold a Manim video folder.")
    parser.add_argument("slug", help="Video folder name, e.g., parallel-machines.")
    parser.add_argument("--title", required=True, help="Human title, e.g., 'Parallel-machine scheduling'.")
    parser.add_argument("--dest", type=Path, default=Path("manim"))
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        sys.exit(f"Slug must be lowercase words joined by hyphens: {args.slug!r}")
    project = Path.cwd().name
    tokens = {"__DATE__": datetime.date.today().isoformat(), "__PROJECT__": project}

    if args.dest.exists():
        print(f"{args.dest} exists; keeping its shared code and render.sh.")
    else:
        shutil.copytree(
            TEMPLATE,
            args.dest,
            ignore=shutil.ignore_patterns(SKELETON, "__pycache__"),
        )
        for path in args.dest.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".sh", ".toml", ".md", ".js"}:
                fill(path, tokens)
        print(f"Copied the template to {args.dest}.")

    video = args.dest / args.slug
    if video.exists():
        sys.exit(f"{video} exists; edit it instead of scaffolding over it.")
    shutil.copytree(TEMPLATE / SKELETON, video)
    module = args.slug.replace("-", "_")
    name = "".join(word.capitalize() for word in args.slug.split("-"))
    (video / "scene.py").rename(video / f"{module}.py")
    tokens |= {
        "__SLUG__": args.slug,
        "__MODULE__": module,
        "__NAME__": name,
        "__TITLE__": args.title,
        "__N__": "TODO",
    }
    for path in video.iterdir():
        fill(path, tokens)
    print(f"Added {video}/ ({module}.py, video.conf, README.md). Output name: {name}.")


if __name__ == "__main__":
    main()
