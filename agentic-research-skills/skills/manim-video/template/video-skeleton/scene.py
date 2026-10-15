"""__TITLE__, in parts.

Each part is a manim-slides Slide, so the same source renders a continuous MP4 per part
(joined into one video by ../render.sh) and a deck with a break at every pause():

    Part1Question    TODO one line per part

Sources: TODO (the lecture notes, the course companion, or the project's exported numbers
file). The assertions below check every displayed number against those sources. Captions,
fonts, and breaks come from ../shared/explainer.py.

    bash ../render.sh __SLUG__ preview|review|final
"""

from manim import FadeIn

from explainer import ExplainerScene, label

# ---------------------------------------------------------------------------
# Computation layer. Every number a scene displays is computed or read here and asserted
# against its source. Nothing below depends on how the scenes draw the results.
# ---------------------------------------------------------------------------

# For a research video, read the project's exported numbers instead of typing them:
#   from pathlib import Path
#   from exported import Numbers
#   PROJECT = Path(__file__).resolve().parents[2]
#   NUMBERS = Numbers(PROJECT / "results/latex/numbers.tex")
#   NUMBERS.check("someEstimate", recomputed_estimate, places=3)

# ---------------------------------------------------------------------------
# Display layer. Colors, layout, captions, and timing live here; fonts and caption rules
# come from ../shared/explainer.py.
# ---------------------------------------------------------------------------


class Part1Question(ExplainerScene):
    def construct(self):
        self.title_card(1, "TODO part title")
        self.say("TODO caption, one or two sentences.")
        self.play(FadeIn(label("TODO")), run_time=0.6)
        self.pause("question")
