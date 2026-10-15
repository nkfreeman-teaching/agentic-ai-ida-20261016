#!/usr/bin/env bash
# Copied from <skills>/manim-video/template on __DATE__.
# Render one video's parts, join them into one continuous MP4, and export the deck.
#   bash render.sh <video> check     run every scene without rendering (asserts, captions,
#                                    layout code), in seconds
#   bash render.sh <video> preview   480p15 draft plus checkpoint stills
#   bash render.sh <video> review    720p15 render plus checkpoint stills for frame review
#   bash render.sh <video> final     1080p30; video and deck copied to <video>/output/
# PARTS="Part2Method Part4Results" bash render.sh <video> review renders only those scenes
# and skips the join and the deck, which need every part.
#
# <video>/video.conf sets, in bash syntax:
#   module=<scene file>.py   name=<output basename>   parts=(<scene class> ...)
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$root"

video="${1:?Usage: bash render.sh <video> [check|preview|review|final]}"
quality="${2:-preview}"
case "$quality" in
    check) options=(--dry_run); resolution=none ;;
    preview) options=(-ql); resolution=480p15 ;;
    review) options=(-r 1280,720 --fps 15); resolution=720p15 ;;
    final) options=(-qh --fps 30); resolution=1080p30 ;;
    *) echo "Usage: bash render.sh <video> [check|preview|review|final]" >&2; exit 2 ;;
esac
# shellcheck source=/dev/null
source "$video/video.conf"
read -r -a scenes <<< "${PARTS:-${parts[*]}}"
# A scene missing from the module makes manim ask which scene to render, which hangs an
# unattended run, so check the names first and give manim no terminal to ask on.
for scene in "${scenes[@]}"; do
    if ! grep -q "^class $scene(" "$video/$module"; then
        echo "$scene (from video.conf or PARTS) is not a class in $video/$module" >&2
        exit 2
    fi
done

build="$root/$video/build/$quality"
mkdir -p "$build"
export PYTHONPATH="$root/shared${PYTHONPATH:+:$PYTHONPATH}"
export CHECKPOINT_DIR="$build/checkpoints"
rm -rf -- "$CHECKPOINT_DIR"
# manim-slides resolves clip paths against this folder's parent, so it must be absolute.
export SLIDES_DIR="$build/slides"
pixi run manim "${options[@]}" --media_dir "$build/media" "$video/$module" "${scenes[@]}" < /dev/null
if [[ "$quality" == check ]]; then
    if compgen -G "$CHECKPOINT_DIR/*.caption-warnings" > /dev/null; then
        cat "$CHECKPOINT_DIR"/*.caption-warnings
    fi
    # FadeOuts that would play without a click before them (shared/explainer.py).
    if compgen -G "$CHECKPOINT_DIR/*.click-warnings" > /dev/null; then
        cat "$CHECKPOINT_DIR"/*.click-warnings
    fi
    if compgen -G "$CHECKPOINT_DIR/*.caption-errors" > /dev/null; then
        cat "$CHECKPOINT_DIR"/*.caption-errors >&2
        exit 1
    fi
    echo "Checked ${scenes[*]}: every scene ran, and nothing was rendered."
    exit 0
fi

videos="$build/media/videos/${module%.py}/$resolution"
if [[ "$quality" != final ]]; then
    for scene in "${scenes[@]}"; do
        rm -rf -- "$build/stills/$scene"
        pixi run python shared/review_frames.py "$videos/$scene.mp4" "$CHECKPOINT_DIR/$scene.json" "$build/stills/$scene"
    done
fi
if [[ "${scenes[*]}" != "${parts[*]}" ]]; then
    echo "Rendered ${scenes[*]} only; skipped the joined video and the deck."
    exit 0
fi

# One continuous MP4. Every part shares codec, size, and frame rate, so the streams are
# copied without re-encoding.
list="$build/parts.txt"
: > "$list"
for scene in "${scenes[@]}"; do
    echo "file '$videos/$scene.mp4'" >> "$list"
done
joined="$build/$name.mp4"
pixi run ffmpeg -loglevel error -y -f concat -safe 0 -i "$list" -c copy "$joined"

# The joined video must last exactly as long as its parts; a dropped or truncated part
# shows up here instead of in front of an audience.
duration() { pixi run ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
parts_total=0
for scene in "${scenes[@]}"; do
    parts_total=$(awk -v a="$parts_total" -v b="$(duration "$videos/$scene.mp4")" 'BEGIN { print a + b }')
done
joined_total=$(duration "$joined")
if ! awk -v a="$parts_total" -v b="$joined_total" 'BEGIN { d = a - b; exit !(d < 0.1 && d > -0.1) }'; then
    echo "Joined video lasts $joined_total s, but its parts sum to $parts_total s." >&2
    exit 1
fi
echo "Joined video: $joined_total s (parts sum to $parts_total s)."

# The deck. --offline copies reveal.js next to the page, so it plays without internet.
deck_dir="$build/deck"
rm -rf -- "$deck_dir"
mkdir -p "$deck_dir"
pixi run manim-slides convert --folder "$SLIDES_DIR" --to html --offline "${scenes[@]}" "$deck_dir/$name.html"
# A corner ring that fills while each slide's clip plays and shows a check when it ends.
pixi run python shared/add_clip_timer.py "$deck_dir/$name.html"

# Each part's first slide, for the video README and for jumping with G in the deck.
start=1
for scene in "${scenes[@]}"; do
    count=$(pixi run python -c 'import json, sys; print(len(json.load(open(sys.argv[1]))["slides"]))' "$SLIDES_DIR/$scene.json")
    echo "$scene starts at slide $start ($count slides)."
    start=$((start + count))
done
echo "Deck: $((start - 1)) slides."

if [[ "$quality" == final ]]; then
    out="$root/$video/output"
    mkdir -p "$out"
    cp -- "$joined" "$out/$name.mp4"
    rm -rf -- "$out/deck"
    cp -r -- "$deck_dir" "$out/deck"
    echo "Saved $video/output/$name.mp4 and $video/output/deck/$name.html"
else
    echo "Saved $joined and $deck_dir/$name.html"
fi
