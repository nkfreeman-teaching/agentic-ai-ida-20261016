# Copied from <skills>/manim-video/template on __DATE__.
"""Extract video frames at a scene's recorded checkpoints and tile them into contact sheets.

    pixi run python review_frames.py VIDEO CHECKPOINTS_JSON OUTPUT_DIR

Called by ../render.sh in review mode.
"""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument("video", type=Path)
parser.add_argument("checkpoints", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

records = sorted(json.loads(args.checkpoints.read_text()), key=lambda record: record["time"])
for record in records:
    record["path"] = args.output / f"{record['time']:07.2f}-{record['name']}.png"
    subprocess.run(
        args=[
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            str(record["time"]),
            "-i",
            str(args.video),
            "-frames:v",
            "1",
            str(record["path"]),
        ],
        check=True,
    )

per_sheet = 6
for start in range(0, len(records), per_sheet):
    sheet = Image.new(mode="RGB", size=(1280, 1170), color="#dddddd")
    draw = ImageDraw.Draw(sheet)
    for offset, record in enumerate(records[start : start + per_sheet]):
        still = Image.open(record["path"])
        still.thumbnail((640, 360))
        x, y = (offset % 2) * 640, (offset // 2) * 390
        sheet.paste(still, (x, y + 30))
        draw.text(xy=(x + 10, y + 6), text=f"{record['name']} | {record['time']:.1f}s", fill="black")
    sheet.save(args.output / f"sheet-{start // per_sheet + 1}.png")
print(f"Extracted {len(records)} checkpoint frames to {args.output}")
