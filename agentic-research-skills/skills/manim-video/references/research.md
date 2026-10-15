# Research videos

A research video explains one result of an open project to a viewer who has not read the
paper. /research-deck covers the static talk; this is the animated explainer, which earns
its cost when motion carries the idea (an estimator built step by step, a comparison that
unfolds, a distribution that shifts).

## Sources and disclosure

- Read the project's `CLAUDE.md`, its plan or manuscript, its results docs, and its numbers
  file before planning. Obey its disclosure rules (for example, a small-cell rule); a video
  is a publication.
- Draw only on exported outputs: the numbers file, exported tables, and exported figures.
  Never read raw data to make a frame.
- Never invent a result, a citation, or the meaning of a figure. Mark a gap as `TODO` in the
  plan and ask.

## Numbers

- Read every displayed number through `exported.Numbers`:
  `NUMBERS.text("name")` gives the string the paper typesets, and the caption uses it
  directly. A rerun of the project's pipeline then reaches the video on its next render.
- A value the video computes itself (a plotted series, a bar height, an interval drawn from
  an exported table) gets `NUMBERS.check("name", computed, places)` when the paper reports
  it, so a stale table and the paper cannot disagree silently.
- Name the numbers file in the module docstring and the video README. If the project has
  several numbers files, pass them all to one `Numbers(...)`.
- A fact with no macro (a date, a named event) is asserted against the manuscript text: a key
  word and the value must share one line of the section that states it (the Tijuana test
  checked five shutdown dates against `introduction.tex` this way).
- Read the project's own definitions before recomputing. In the Tijuana test the percent was
  `expm1` of the estimate and the fit error was the root mean square of the pre-period gaps,
  both found in the project's scripts; a guess at either would have failed its `check`.
- Assert the project's disclosure rule on every plotted series, e.g., `min(count) >= 10` for
  a small-cell rule, so a rerun that drops a cell below the threshold fails the render.
- Read exported tables with polars (in the template environment). Plot only tables behind a
  figure the project has already exported, since those passed its disclosure step.

## What the test covered

The research path was tested on isg-fosta-tijuana (Oct 12, 2026): a five-part, 114-second
video with 17 slides, built from `results/latex/numbers.tex` and three exported parquet
tables. Importing its module runs 11 macro checks against recomputed values, five date
checks against the manuscript, and 14 other asserts (table structure, the disclosure rule,
and claims the captions make, such as "above the synthetic line in all 12 months"). Patterns it did not
exercise: `MathTex`, an `ImageMobject` of an exported figure, and a project with several
numbers files.

## Parts

A research video usually has five to seven parts, each a few minutes or less:

1. The background, i.e., the setting a viewer needs before the question makes sense: what
   the program, market, or system is, who the actors are, how the process works step by step,
   and what each unit the video counts actually is. Draw it as a process (a flow of steps or
   actors), not as a list of definitions, and take the definitions from the manuscript's
   introduction and background sections. This part is required, and it is the one most often
   skipped by a plan built from the results.
2. The question, in the viewer's terms.
3. The data, i.e., what was observed, over what period, and what one unit of observation is.
4. The method, built up in the order a viewer needs it.
5. The main result, with its size stated against something the viewer can picture.
6. One check on the result (a placebo, a robustness run, a comparison group), only if it
   changes how far the viewer should trust part 5.
7. What the result means, and its main limit, in one part.

The h2a-enforcement video (Oct 12, 2026) first shipped without a background part. It
used "H-2A", "certified position", and "WHD case" from its first frame without
defining them, and its owner judged it hard to follow for a general viewer.

The plan is a proposal; confirm it with the user before building.

## Visual pieces

The skill carries no plots. Each research video builds its own pieces in its module (axes
from manim's `Axes`, bars as `Rectangle`s, an estimate with its interval as a dot and a line),
fed from exported tables, so they can animate. A static exported figure can appear through
`ImageMobject`, but then it cannot move, so prefer redrawing what the video animates.
Label every axis and series in Nimbus Roman through `label`, and keep a series' color
fixed across parts.
