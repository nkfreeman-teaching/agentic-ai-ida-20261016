# Conventions

These rules came out of the first videos built with this skill in October 2026 (a teaching
video on parallel-machine scheduling, called OM-522 below, and several research explainers,
such as the Tijuana and H-2A videos). The template already enforces the ones marked
"enforced"; the rest are for the scene code each video writes.

## Two layers in every video module

- The computation layer recomputes or reads every displayed number and asserts it against
  the source (lecture notes, a course companion, or a research project's exported numbers).
  Importing the module runs the asserts, so a changed source fails the render instead of
  shipping a wrong number.
- The display layer holds colors, layout, captions, and timing. It never computes a result.
  A caption builds its numbers from computation-layer values with f-strings, never typed
  digits.
- A video's visual pieces (a Gantt chart, a plot, a results table) live in its own module,
  as classes that only build mobjects. The scene owns every animation.

## Text

- Text uses Nimbus Roman, and `explainer.py` refuses to run if the font is missing, because
  Pango substitutes another face silently (enforced). Nimbus Roman lacks ceiling brackets
  and check marks, so check any math glyph with `fc-list ":charset=2308"` (the hex code
  point) before using it.
- Small text is built at four times its size and scaled down, and it is rebuilt at a smaller
  factor when Pango wraps a long string silently (enforced in `label` and `markup`).
- Captions have at most two lines, split at a sentence boundary, and `make_caption` raises
  an error on copy that would need shrinking below 90 percent (enforced). Shorten the
  sentence; never lower the limit.
- One caption line at the default size (30) holds about 69 characters, i.e., 11.8 frame
  units (the limit since Oct 15, 2026; it was 12.8, about 75 characters, measured on the
  Tijuana test, where 72 characters came to 12.2 units). A one-sentence caption longer than
  that fails, and a two-sentence caption with a longer sentence shrinks, which leaves
  captions at uneven sizes. `render.sh <video> check` lists both kinds in one pass.
- Captions hang from a fixed top edge (`CAPTION_TOP`), so a second line grows downward and
  the first line never jumps between a one-line and a two-line caption (enforced).
- Never `scale_to_fit_width` a label unconditionally, since it enlarges short strings to the
  target width. Shrink only when the label is wider than its slot.
- Anchor rows of text by an edge (`move_to(point, aligned_edge=UP)`), because center-anchored
  text of different heights drifts.
- Change a number or label by cross-fading (`FadeOut(old)` and `FadeIn(new)` in one `play`,
  then reassign the reference), never `Transform` between two `Text` objects. `Transform`
  morphs glyph outlines through unreadable shapes for the whole transition; the OM-522 deck
  showed "Makespan 10" becoming "Makespan 9" as a scramble when paused mid-slide.
- Pango markup gives subscripts and superscripts (`C<sub>max</sub>`). `MathTex` needs the
  system LaTeX (`latex` and `dvisvgm`, present on the machine the skill was built on), renders in Computer Modern
  rather than Nimbus Roman, and is worth it only for a displayed equation.

## Layout and animation

- Layering uses z-index constants declared once per module, never `bring_to_back` (manim
  0.22 has no `add_to_back`). Give axis labels and tick text a z-index above any shaded band,
  since a band added later covers text at the same z-index (the Tijuana test lost its "2018"
  label this way).
- Draw a jagged series (a monthly count) as a solid line and tell series apart by color and
  width. `DashedVMobject` on a jagged polyline breaks into faint dots.
- Leave about 0.4 units between the caption's bottom (about 2.95 for two lines) and the
  highest label in the scene, or labels touch the second caption line.
- A moving object that passes others gets a higher z-index for the move, then drops back.
- Fading a group fades each member, so overlapping opaque shapes turn translucent and show
  edges behind them. Fade a full-frame cover over the content instead, remove the content,
  then remove the cover.
- Python makes a name local for the whole function once it is assigned, so a helper named
  `card` and a local variable named `card` collide with an UnboundLocalError far from the
  cause. Name helpers with verbs (`make_card`).
- `pause(name)` records the review checkpoint and calls `next_slide()` in one call, so the two
  lists cannot drift apart (enforced). Every caption change and every helper that moves
  something should call `mark()`, with an offset into the motion for mid-transition stills.
- `READ` (2.2 s) is the hold before each break, so the continuous MP4 reads without a
  presenter. A part ends on a caption held about 3.5 s.
- A faster cut (a pitch sent by email) sets the scene class attributes `pace`, `read`, and
  `cps` instead of editing the constants. With `cps` set, a break holds until the caption
  has been on screen for its length divided by `cps` seconds, so a lower `pace` never cuts a
  long caption short. A research pitch video used `pace = 0.85`, `read = 1.5`, and
  `cps = 17`, which took a 5.5-minute explainer's material to a 2:40 cut.

## Clicks and pace (author's ruling, Oct 12, 2026)

- **Nothing leaves the screen without a click.** A presenter talks at their own speed, and a
  caption that is replaced mid-sentence forces them to step back through the deck. Adding to
  the picture may roll on (new text below, a block moving into its slot); replacing a caption,
  clearing the stage, removing an object, or moving existing content waits for a click.
- `say()` and `clear_stage()` enforce this: they call `pause()` first when anything has played
  since the last break (enforced). A first caption and a caption right after a break roll on.
- Other removals live in scene code, so `render.sh <video> check` lists every `FadeOut` that
  would play after other content with no break between (a `.click-warnings` file per scene).
  Fix each by adding a `pause()` before it, or by folding the removal into the first animation
  after an existing break. A check with warnings left is not done.
- `with self.rolling():` exempts animations that finish a placement, i.e., a queued block
  moving into its slot and the highlight that clears after it. Use it for nothing else.
- Placements roll on even when a run of them is long (an LPT run of seven jobs is one segment).
  A step whose own caption names the move gets a click per step, because the caption changes.
- **`PACE` (1.25) stretches every animation and wait**, so motion is slow enough to talk over.
  Scenes keep writing natural run times; `play()` scales them, and `Scene.wait()` goes through
  `play()`, so do not scale waits a second time. Checkpoint offsets scale with it in `mark()`.
- Scaled run times are rounded to whole frames. At 15 fps a 0.75 s run time renders a frame
  long, and on the OM-522 deck the checkpoints drifted about 0.4 s behind the video within one
  part, so review stills caught captions mid-crossfade.
- Expect more clicks than breaks you write by hand. On the OM-522 session 15 deck the rule
  took the deck from 48 to 87 slides.

## Rendering

- `render.sh` has four modes: check (a manim `--dry_run` of every scene, which runs the
  computation layer, every caption, and the layout code without writing video), preview
  (480p15 plus contact sheets), review (720p15 plus contact sheets), and final (1080p30).
  `PARTS="..."` renders selected scenes and skips the join and the deck. On the Tijuana test,
  check took about 1 minute and preview about 50 seconds for a 114-second video.
- `render.sh` refuses a scene name that the module does not define and gives manim no
  terminal, because a missing scene otherwise makes manim prompt for a choice, which hangs an
  unattended run.
- Launch review and final renders in the background with a timestamped log and an `EXIT=`
  sentinel. The sentinel is the result; the harness once reported success for a run whose
  sentinel read `EXIT=1`.
- Measured times on the machine the skill was built on: the 282-second OM-522 video took about 2.5 minutes at
  review quality and about 3.5 minutes at final quality (log start and end times).
- Building `Text` outside a render (for example in `python -c`) writes a `./media` text
  cache in the working directory. Delete it afterward.

## manim-slides 5.7.0 on manim 0.22 (tested Oct 12, 2026)

- manim-slides does not run on manim 0.22 as shipped, because it writes
  `config["write_to_movie"]` and `config["flush_cache"]` (both removed in 0.22) and sets
  `max_files_cached` to infinity (0.22 accepts only integers). `ExplainerScene` overrides
  `__init__` and `render` to avoid all three (enforced). Remove the override once
  manim-slides supports 0.22, and update this file and the template together.
- manim 0.22 fixes `max_files_cached` when the scene is constructed, so `ExplainerScene.__init__`
  sets it to -1 before `Scene.__init__` runs; a part with more than 100 animations otherwise loses
  partial clips before manim-slides reads them (st-geo-robust-siting, Oct 14, 2026, enforced).
- `manim-slides convert --to html` loads reveal.js from cdn.jsdelivr.net unless it is given
  `--offline` (enforced in `render.sh`).
- The slide JSON stores clip paths as the scene saw them, and `convert` resolves them
  against the slides folder's parent, so `SLIDES_DIR` must be absolute (enforced).
- `skip_reversing = True` saves rendering the reversed clips that only the Qt player uses,
  since the HTML deck plays every slide forward (enforced).
- A presenter cannot tell a clip that is still playing from one that has ended, because a
  slide often holds still for its last second or two (author's request, Oct 14, 2026). The deck
  therefore has an animation timer in the bottom-right corner: a gray ring that fills while
  the clip plays, dims while Space has paused it, and becomes a white check on a gray disk
  when the clip ends. T hides or shows it. `render.sh` adds it after `manim-slides convert`
  with `shared/add_clip_timer.py`, which also updates an existing deck without re-rendering,
  and `check_deck.py` fails a deck that lacks it (enforced). The timer reads the current
  slide's background video each frame, so it needs no change when manim-slides adds slides.
  Its corner is free because the deck turns off reveal.js's controls, progress bar, and slide
  number; turning any of them on would put it under the timer.

## Grounding (author's ruling, Oct 12, 2026)

A silent video has no speaker to answer "what does that mean?", so every term a viewer
needs is on screen before the video relies on it. The audience is a general viewer, i.e.,
someone outside the field who has not read the source, unless the user names another.

- **The grounding table is part of the plan.** One row per term with its plain-language
  definition, the source line it comes from, and the part where it first appears. Collect
  terms by reading every planned caption, label, axis title, and panel heading. Include
  acronyms (WHD, OFLC), named programs and institutions (H-2A, the Department of Labor),
  units of observation (a case, a certified position, a position-year), time conventions (a
  fiscal year, a findings end year), and statistical devices a viewer reads off the frame (a
  95% interval, a log axis, a weighted average, a decomposition term).
- **Define in plain words, then use the term.** Write the definition as an ordinary sentence
  ("A certified position is a job the government allows the employer to fill with an H-2A
  worker"), then the term alone afterward, never a synonym. Spell out an acronym in the
  caption on first use, with the acronym in parentheses.
- **Say what a unit is not** when a viewer could mistake it for something nearby ("not a worker
  who arrived", "a civil finding, not a crime"). These contrasts usually carry the paper's
  scope limits.
- **Ground the setting with a process, not a glossary.** The background part animates how the
  setting works (actors and steps in order), and each definition appears at the step where
  its object enters. A list of terms on a card is a fallback for terms with no step.
- **Ground statistical devices where they first appear.** Gloss an interval, a log axis, or a
  weighted average in the caption or a label of the frame that first draws it ("each
  gridline is ten times the one below"), not in a separate part.
- **Assert the facts in a definition.** A definition that states a fact (a share, a count, a
  rule such as "three-fourths of the contract hours") is asserted against the source line
  that states it, like any number (see `research.md` for manuscript-line asserts). A fact the
  source cites from elsewhere names that source on screen.
- **Do not define twice.** Once a term is grounded, later captions use it plainly; repeated
  definitions take caption space a later point needs.

## Visual polish (author's ruling and three-reviewer pass, Oct 15, 2026)

These came from the author's review of a research explainer and a blind pass over
the stills of its pitch cut by Opus, Sonnet, and Codex, each finding verified against the
frames before it was adopted. They apply to every new video.

- **Outline every filled bar** with a thin black stroke (about 1.2), so bars read against
  white and against shaded bands. Shaded regions (a window, a thicket) stay unstroked.
- **Center multi-line text blocks** with `text_block`. A block at the middle of the frame
  reads as ragged when its lines are left-aligned. Keep left alignment for bulleted lists
  and table columns only.
- **Keep everything at least 0.5 units inside the frame edges**, labels included, and assert
  it where a label's width depends on its text (a series name right-aligned to an axis).
- **Center each step's final composition between the caption and the footnote slot**
  (about y = -0.45), and place earlier elements in their final slots so nothing jumps.
- **One box style.** One stroke width (2), one corner radius (0.12), equal padding, and three
  text roles: title 26, body 22, source 18 muted, always in that order. Boxes in one row or
  column share a width and a height. Neutral borders are mid-gray (about #9A9A9A), and a
  colored border means a category.
- **Parallel items get parallel containers.** Two cited studies are both boxed; two
  statistics are both cards of one size.
- **On-screen text adds what the caption does not** (a number, a name, a source, a label on
  a drawn object). Never repeat the caption's sentence on screen.
- **A caption's claim needs a visible change.** If a caption says growth came from one
  component, split the bar; a settled frame identical to the one before reads as a dropped
  animation.
- **Light category colors get a darker text tone.** Amber (#E69F00) has about 2.2:1 contrast
  on white, so amber text uses about #9A6700 (4.9:1) and the light value stays for fills.
- **Category colors keep their meaning in every part.** Ordered groups (decades) use an
  ordered single-hue ramp that reuses no category color.
- **Chart text has three sizes**: ticks 20, axis titles 22, data labels 22. Nothing that must
  be read is smaller than 18. A chart's metric title sits beside its plot (above it,
  left-aligned at the baseline's start), never floating mid-height without an axis.
- **Under a chart the rows run tick labels, then group sizes ("n = 246"), then the axis
  title**, so each count sits under its group.
- **Text over gridlines, shading, or a reference line gets a white backing plate**
  (`with_backing`), including direct data labels and bar labels.
- **Legends sit outside the plot area**, in one row above it; side notes go to the footnote
  slot.
- **An interval sits on or directly beside what it describes**, with its estimate marked.
- **One footnote slot** (`footnote()`, centered at y = -3.6, size 18, muted) for sources and
  "Illustration" notes.
- **Connectors share one arrowhead size** (`tip_length` about 0.2) and run from parent
  bottom-center to child top-center; an annotation on a filter step sits beside the arrow,
  not in its path.
- **Typography**: a true minus sign (U+2212) in tick labels; straight quotes and apostrophes
  (the author's style rule overrides a reviewer preference for curly ones).
- **A video sent to someone cold opens and closes on a title card** with the title, authors,
  affiliations, and the work it builds on.

## Frame review

- Review at 720p or higher, and read every contact sheet as an image. A clean exit code is
  not a visual review.
- Check each sheet for clipped or overlapping text, a caption that wraps to three lines,
  objects outside the frame, a label that collides with a line, stale objects left from an
  earlier step, color that carries meaning without a label, and mid-transition frames that
  scramble text.
- Read the sheets in order as a viewer who has not read the source, and list every term,
  acronym, or unit that appears before its definition. Each one is a defect, fixed by moving
  or adding the definition, not by assuming the viewer knows it.
- A reviewer (a subagent or Codex) repeats what the pixels show and sometimes invents
  content. Check each claim against the frame and the source before applying it. On a
  research pitch video, one reviewer placed the clipped timeline labels in the wrong parts
  and another misread a label, though both underlying defects were real.
- Check each frame against "Visual polish" above as well as this list.

## Desktop automation (Qt player or a manual deck test)

`scripts/check_deck.py` replaces desktop automation for the deck. If the Qt player or a
manual browser test is needed anyway:

- Find windows by process ID, never by title, since the terminal title contains "Manim".
- Confirm `xdotool` focus before sending keys.
- `pkill -f` with a pattern kills its own shell, so kill by PID.
