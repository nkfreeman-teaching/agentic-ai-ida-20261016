---
name: manim-video
description: "Builds a silent animated Manim video from one source as two products, a continuous MP4 and an offline HTML deck (manim-slides) that stops at each break until the presenter advances it, for teaching a concept or explaining a research result. Agrees the parts and breaks with the user, asserts every displayed number against its source (lecture notes or a research project's exported numbers), reviews contact sheets as images, and checks that the deck plays offline. Use when the user asks for a Manim video, an animated explainer, a video walkthrough of a concept or result, or a video that also works as a click-through deck."
---

# manim-video

A video built with this skill is silent, so captions carry the words and the animation carries
the idea. One scene module renders both products: the continuous MP4 for viewers on their own,
and a deck for a presenter, where each `pause()` becomes a stop.

The skill carries the process and the render setup, not the visuals. A video's own pieces (a
Gantt chart, a plot, an equation panel) live in its scene module. `<skills>` below means the
folder that holds this skill.

The parts of a video are called "parts", never "chapters".

## Requirements

- [pixi](https://pixi.sh), which installs manim, manim-slides, ffmpeg, Cairo, and Pango into
  the project's `manim/` folder. The template was tested on Linux; the other platforms in
  `template/pixi.toml` are listed but untested.
- The Nimbus Roman font (Debian and Ubuntu package `fonts-urw-base35`; on macOS or Windows,
  install the `.otf` files from https://github.com/ArtifexSoftware/urw-base35-fonts).
  `template/shared/explainer.py` refuses to run without it, because Pango substitutes another
  face silently. To use another font, change `FONT` there.
- Bash, since `render.sh` is a bash script. macOS and Linux have it; on Windows, run the
  renders under WSL or Git Bash.
- For the offline deck check only: Python with `playwright` and Chrome or Chromium (set
  `CHROME_PATH` if Chrome is not at `/usr/bin/google-chrome`).

## Mode

| Found | Mode |
|---|---|
| no `manim/` folder in the project | **Create** (all steps) |
| a `manim/` folder from this template, but no folder for this video | **Create** (all steps) |
| the video's folder exists | **Revise**: read its module and README, then start at step 4, 5, or 6 as the request needs |

Teaching or research is decided by the sources: lecture notes make a teaching video; a project
with exported results makes a research video. For research, read `references/research.md` as well.

## Rules

- **Every displayed number is asserted.** The computation layer recomputes or reads each number
  and asserts it against its source, and importing the module runs the asserts. Captions take
  numbers from computation-layer values, never typed digits.
- **Display choices stay out of the computation layer.** Colors, layout, captions, and timing are
  in the display layer, so a wording change never touches a result.
- **Nothing leaves the screen without a click.** Replacing a caption, clearing the stage, removing
  an object, or moving existing content waits for a break; adding may roll on. `say()` and
  `clear_stage()` enforce it, and `check` lists the remaining unclicked removals, which must be
  zero (see "Clicks and pace" in `references/conventions.md`).
- **Every term is grounded before it is used.** The viewer has not read the source. Each term,
  acronym, institution, and unit that appears on screen is defined in plain words at or before
  its first appearance, and a research video opens with a background part on the setting.
- **Parts and breaks are the user's call.** Agree them with the user before writing scenes.
- **A clean exit is not a review.** Look at every contact sheet and both deck screenshots as
  images. An agent that cannot read images says so and asks the user to look.
- **Never commit** in the project. Report the files; the user commits.

## Create

1. **Read the sources and the conventions.** Read the sources the video teaches from or, for
   research, the project's plan or manuscript, results, and numbers file. Read
   `references/conventions.md`.
2. **Plan the grounding and the parts.** List every term the video will put on screen that a
   general viewer may not know, with its plain-language definition, its source, and the part
   where it first appears. Then draft one row per part with the scene class name
   (`Part1Background`), what it shows, every number it displays with that number's source, and
   where its breaks fall. Show both tables to the user and ask for approval, together with any
   open inclusion questions, each with your recommendation. Write no scenes until the plan is
   approved.
3. **Scaffold.** From the project root run
   `python <skills>/manim-video/scripts/scaffold.py <slug> --title "<Title>"` (standard library
   only). The first run copies the template to `manim/`; each run adds `manim/<slug>/`. Then run
   `pixi install --manifest-path manim/pixi.toml`. Set `parts=(...)` in `manim/<slug>/video.conf`
   to the approved scene classes. Add the video's row to `manim/README.md`.
4. **Build the computation layer.** Write the data, the functions that compute what the scenes
   show, and an assert for every displayed value against its source, with a comment naming the
   source's section or table. Confirm the asserts run by importing the module:
   `cd manim && PYTHONPATH=shared:<slug> pixi run python -c "import <module>"`. An assert that
   fails is a finding about the source or the computation; resolve it before drawing.
5. **Build the display layer, check it, and sample it.** Write the scenes with the helpers in
   `shared/explainer.py` (`title_card`, `say`, `pause`, `mark`, `clear_stage`). Keep each caption
   sentence to about 75 characters. From `manim/`, run `pixi run render <slug> check` after every
   round of scene edits: it runs every scene without rendering and lists every caption too wide to
   fit, every caption that would shrink, and every removal that would play without a click. Then
   render the first part alone, `PARTS="<first scene class>" pixi run render <slug> preview`, and
   look at its contact sheets in `<slug>/build/preview/stills/`. Fix what breaks, then render every
   part at preview quality and look at every sheet.
6. **Review render.** Run `pixi run render <slug> review`, redirected to a log, and capture the
   exit code. Look at every contact sheet in `<slug>/build/review/stills/` against the frame review
   list in `references/conventions.md`. Fix layout defects, run `check`, and re-render only the
   changed parts with `PARTS=...` until the sheets are clean.
7. **Final render.** Run `pixi run render <slug> final` the same way. `render.sh` fails if the
   joined MP4's length differs from the sum of its parts by more than 0.1 s, and it prints each
   part's first slide and the deck's slide count. Report the exit code.
8. **Check the deck offline.** Run
   `python <skills>/manim-video/scripts/check_deck.py manim/<slug>/output/deck/<Name>.html --expect <slides> --shots <a scratch folder>`.
   It blocks every network request, decodes every slide's video, tests the right arrow and the
   G-number-Enter jump, and checks the animation timer. Look at both screenshots. Exit 1 is a
   defect to fix.
9. **Fill the video README** (`manim/<slug>/README.md`): each part, its first slide from step 7,
   and its source. Describe what each part shows without typing its results, since a typed number
   goes stale when the source changes and the README has no assert.

## Revise

Read the video's module, README, and `video.conf`. A wording or layout change starts at step 5
for the touched parts (run `check` first); a changed source or number starts at step 4. A change
to the parts list or the breaks is a plan change, so confirm it as in step 2. Finish with steps 7
to 9, since slide numbers move when a break is added or removed.

## Final report

Report the MP4 path with its resolution, frame rate, and length; the deck path with its slide
count and each part's first slide; the exit codes; what the frame review covered and fixed; and
the deck check's result. Name what was not checked, for example the deck on the presenting
machine.

## Resources

- `template/` is copied to the project's `manim/` folder by `scripts/scaffold.py`:
  `shared/explainer.py` (font check, colors, caption builders, and `ExplainerScene` with the
  manim-slides patch), `shared/review_frames.py` (contact sheets), `shared/exported.py` (reads a
  LaTeX numbers file), `shared/clip_timer.js` and `shared/add_clip_timer.py` (the deck's
  animation timer), `render.sh` (check, preview, review, and final modes), `pixi.toml`,
  `README.md`, and `video-skeleton/`.
- `scripts/scaffold.py` copies the template and adds a video folder.
- `scripts/check_deck.py` checks that a deck plays offline.
- `references/conventions.md` holds the text, layout, rendering, manim-slides, and frame review
  rules.
- `references/research.md` holds the rules for research videos.
