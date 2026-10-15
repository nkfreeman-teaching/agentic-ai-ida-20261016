# Manim videos

Silent animated videos for __PROJECT__, one folder per video. Each video is built from one
source as two products: a continuous MP4 and an offline HTML deck that stops at each break
until the presenter advances it. The setup was copied from
`<skills>/manim-video/template` on __DATE__.

| Folder | Video |
|---|---|

## Layout

- `shared/explainer.py` holds what every video uses: the font check, base colors, text and
  caption builders, formula panels, and `ExplainerScene` (captions, checkpoints, slide
  breaks, and part title cards).
- `shared/review_frames.py` cuts checkpoint stills into contact sheets for review.
- `shared/exported.py` reads the project's exported numbers file, so a video displays the
  values the paper displays.
- `shared/clip_timer.js` is the deck's animation timer, and `shared/add_clip_timer.py` adds
  it to a deck (`render.sh` runs it after every deck build).
- `render.sh` renders one video folder. Each video folder has its scene module, a
  `video.conf` naming the module, the output name, and the parts in order, and a README
  naming its sources.
- `pixi.toml` is a separate environment (manim 0.22, manim-slides 5.7.0 with PyQt6), so the
  project's own environment does not depend on it.

Renders stay out of git (`*/build/`, `*/output/`).

## Render

From this folder:

```bash
pixi run render <video> check     # run every scene without rendering; lists caption defects
pixi run render <video> preview   # 480p15 draft plus contact sheets in <video>/build/preview/
pixi run render <video> review    # 720p15 plus contact sheets in <video>/build/review/stills/
pixi run render <video> final     # 1080p30, video and deck in <video>/output/
PARTS="Part1Question" pixi run render <video> review
```

The last form renders selected parts only and skips the joined video and the deck. Each
video module asserts every displayed number against its source before drawing, so a changed
source fails the render instead of shipping a wrong number.

## Presenting

Copy `<video>/output/deck/` (the page and its `_assets/` folder) to the presenting machine
and open the HTML file in a browser. The right arrow plays the next segment, and the left
arrow returns to the previous one. Typing `G`, a slide number, and Enter jumps to that
slide. The deck needs no internet, because the render copies reveal.js into the assets
folder.

A small ring in the bottom-right corner fills while the current slide's animation plays and
becomes a check when it has finished, so the next click is safe. Space pauses and resumes
the animation (the ring dims while paused), and T hides or shows the ring.
