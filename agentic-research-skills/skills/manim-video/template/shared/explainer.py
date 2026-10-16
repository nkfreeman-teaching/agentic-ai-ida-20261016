# Copied from <skills>/manim-video/template on __DATE__.
"""Display conventions shared by every video in this folder.

A video module imports from here and adds its own visual pieces (a Gantt chart, a plot, an
equation panel). Nothing here knows about any topic.

    from explainer import INK, MUTED, ExplainerScene, label, markup

render.sh puts this folder on PYTHONPATH.
"""

import contextlib
import functools
import json
import os
from pathlib import Path

import manimpango
from manim import (
    DOWN,
    LEFT,
    UP,
    WHITE,
    FadeIn,
    FadeOut,
    ManimColor,
    MarkupText,
    Rectangle,
    Scene,
    Text,
    VGroup,
    config,
)
from manim.animation.animation import Wait, prepare_animation
from manim_slides import Slide
from manim_slides.slide.base import BaseSlide

config.background_color = WHITE

FONT = "Nimbus Roman"
# Pango silently substitutes a default face for a missing family. Nimbus Roman ships in the
# urw-base35 fonts (Debian and Ubuntu package fonts-urw-base35). It has no ceiling brackets
# or check marks, so check a math glyph with fc-list ":charset=<hex>" before using it.
if FONT not in manimpango.list_fonts():
    raise RuntimeError(f"Font not installed: {FONT} (Debian or Ubuntu: fonts-urw-base35; macOS or Windows: github.com/ArtifexSoftware/urw-base35-fonts)")
INK = ManimColor("#222222")
MUTED = ManimColor("#6B6B6B")
FAINT = ManimColor("#B0B0B0")
ACCEPT = ManimColor("#027A5A")
ALERT = ManimColor("#D55E00")

CAPTION_Y = 3.4
# Captions hang from a fixed top edge, so a second line grows downward and the first line
# never jumps when a caption changes between one and two lines; the top sits 0.38 units
# (about 34 px at 720p) below the frame edge (polish review, 2026-10-15).
CAPTION_TOP = 3.62
CAPTION_SIZE = 30
# 11.8 units is about 83% of the frame; a one-line caption that runs edge to edge looks
# crowded (three-reviewer polish pass on a research pitch, 2026-10-15; was 12.8).
CAPTION_MAX_WIDTH = 11.8
# A caption that would need shrinking below this factor is a copy defect, not a layout one.
CAPTION_MIN_SCALE = 0.9
PANEL_SIZE = 26
FOOTNOTE_Y = -3.6

# Seconds a caption stays up before a break, so the continuous MP4 is readable on its own.
# The deck stops at the break anyway.
READ = 2.2

# Every animation, wait, and checkpoint offset runs PACE times as long as the scene code
# says, so a presenter can talk over the motion (1.25 since Oct 12, 2026). A video sets its
# own pace and hold as the scene class attributes `pace` and `read` (2026-10-15).
PACE = 1.25

# manim-slides stores clip paths as given and resolves them against this folder's parent,
# so render.sh passes an absolute path.
SLIDES_DIR = Path(os.environ.get("SLIDES_DIR", "slides"))

# Pango spaces glyphs unevenly at small sizes, so text is built at SUPERSAMPLE times its
# size and scaled down.
SUPERSAMPLE = 4


@functools.cache
def _line_height(size):
    return Text("Mg", font=FONT, font_size=size).height


def _one_line(kind, text, size, color):
    """Build at SUPERSAMPLE times the size, then fall back to smaller factors if Pango
    wrapped the long string onto a second line."""
    reference = _line_height(size)
    for factor in (SUPERSAMPLE, 2, 1):
        mob = kind(text, font=FONT, font_size=size * factor, color=color).scale(1 / factor)
        if mob.height < 1.6 * reference:
            return mob
    raise ValueError(f"Text wraps even at its natural size: {text!r}")


def label(text, size=24, color=INK):
    return _one_line(Text, text, size, color)


def markup(text, size=24, color=INK):
    """Text with Pango markup, for subscripts such as C<sub>max</sub>."""
    return _one_line(MarkupText, text, size, color)


def make_caption(text, min_scale=CAPTION_MIN_SCALE, max_width=CAPTION_MAX_WIDTH):
    """One line when it fits, otherwise two lines split at the sentence boundary that
    best balances their widths. Refuses copy that would need shrinking below min_scale."""
    line = label(text, size=CAPTION_SIZE)
    if line.width <= max_width:
        return line.move_to([0, CAPTION_TOP, 0], aligned_edge=UP)
    sentences = [part.strip() for part in text.replace(". ", ".\n").replace("? ", "?\n").split("\n")]
    if len(sentences) < 2:
        raise ValueError(
            f"Caption is one sentence too wide for one line ({line.width:.1f} > {max_width}): {text!r}",
        )
    splits = [
        (" ".join(sentences[:cut]), " ".join(sentences[cut:])) for cut in range(1, len(sentences))
    ]
    first, second = min(splits, key=lambda pair: abs(len(pair[0]) - len(pair[1])))
    lines = VGroup(label(first, size=CAPTION_SIZE), label(second, size=CAPTION_SIZE)).arrange(
        DOWN,
        buff=0.12,
    )
    if lines.width > max_width:
        if max_width / lines.width < min_scale:
            raise ValueError(
                f"Caption needs a shorter sentence ({lines.width:.1f} > "
                f"{max_width / min_scale:.1f}): {text!r}",
            )
        lines.scale_to_fit_width(max_width)
    return lines.move_to([0, CAPTION_TOP, 0], aligned_edge=UP)


def text_block(lines, size=24, color=INK, buff=0.16):
    """Lines of text stacked and centered on one another. A block placed at the middle of
    the frame reads as ragged when its lines are left-aligned, so center by default; keep
    left alignment for bulleted lists and table columns (author's ruling, 2026-10-15)."""
    return VGroup(*(label(line, size=size, color=color) for line in lines)).arrange(DOWN, buff=buff)


def with_backing(mob, buff=0.05):
    """Put a white plate behind text that sits over gridlines, shading, or a reference
    line, so the line does not strike the glyphs through (polish review, 2026-10-15)."""
    plate = Rectangle(
        width=mob.width + 2 * buff,
        height=mob.height + 2 * buff,
        stroke_width=0,
        fill_color=WHITE,
        fill_opacity=1,
    ).move_to(mob)
    return VGroup(plate, mob)


def footnote(text):
    """A source or disclosure note in the one footnote slot, centered at the frame's
    bottom (polish review, 2026-10-15)."""
    return label(text, size=18, color=MUTED).move_to([0, FOOTNOTE_Y, 0])


def formula_panel(lines, x, top_y, size=PANEL_SIZE):
    """Left-aligned lines of markup, top edge at top_y."""
    group = VGroup(*(markup(line, size=size) for line in lines)).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.22,
    )
    return group.move_to([x, top_y, 0], aligned_edge=UP + LEFT)


def _whole_frames(seconds):
    """Round a run time to whole frames. A run time between frames renders a frame longer
    than self.time records, and over a part the checkpoints drift behind the video."""
    return max(1, round(seconds * config.frame_rate)) / config.frame_rate


def _fades_out(animation):
    """True for a FadeOut, alone or inside a group such as LaggedStart."""
    if isinstance(animation, FadeOut):
        return True
    return any(_fades_out(part) for part in getattr(animation, "animations", []))


class ExplainerScene(Slide):
    """Caption, checkpoint, and break helpers for one part of a video.

    Every caption change and break records a checkpoint time, and tear_down writes them to
    $CHECKPOINT_DIR/<Scene>.json so review_frames.py can pull settled and mid-transition
    stills. pause() places a checkpoint and a slide break in one call, so the two lists
    cannot drift apart.

    Nothing leaves the screen without a click. say() and clear_stage() add a break first
    when anything has played since the last one, and a dry run (render.sh check) lists
    every other FadeOut that would play without a click, so the scene can add one.
    rolling() exempts animations that finish a placement.

    manim-slides 5.7.0 predates manim 0.22, which removed config["write_to_movie"] and
    config["flush_cache"] and made max_files_cached integer-only. __init__ and render
    below replace the two Slide methods that touch those settings. Remove them once
    manim-slides supports manim 0.22.
    """

    # The HTML deck plays each slide forward only, so the reversed clips the Qt player
    # uses are not worth their render time.
    skip_reversing = True
    # Run-time multiplier and hold before a break; a faster cut (a pitch) lowers both.
    pace = PACE
    read = READ
    # Reading speed in caption characters per second. When set, a break holds until the
    # current caption has been on screen for len(caption) / cps seconds of video, never less
    # than `read`, so a long caption is not cut off when `pace` is low. None keeps the
    # fixed hold (2026-10-15).
    cps = None
    # Widest one-line caption, in frame units.
    caption_max_width = CAPTION_MAX_WIDTH

    def __init__(self, *args, **kwargs):
        # manim 0.22 copies max_files_cached into the file writer's settings in
        # Scene.__init__, so the override in render() comes too late, and a part with more
        # than 100 animations loses its oldest partial files before manim-slides reads them
        # (st-geo-robust-siting, 2026-10-14). -1 leaves the cache unlimited.
        config["max_files_cached"] = -1
        # BaseSlide.__init__ continues to Scene.__init__ through the MRO, skipping the
        # write_to_movie line in Slide.__init__.
        BaseSlide.__init__(self, *args, output_folder=SLIDES_DIR, **kwargs)

    def render(self, *args, **kwargs):
        max_files_cached = config["max_files_cached"]
        config["max_files_cached"] = -1  # manim-slides reads every partial movie file
        try:
            Scene.render(self, *args, **kwargs)
        finally:
            config["max_files_cached"] = max_files_cached
        if config["dry_run"]:
            return  # render.sh check: nothing was written, so there are no slides to save
        self._save_slides(
            use_cache=not (config["disable_caching"] or self.disable_caching),
            flush_cache=self.flush_cache,
            skip_reversing=self.skip_reversing,
        )

    def setup(self):
        self.caption = None
        self.caption_chars = 0
        self.caption_shown_at = 0.0
        self.checkpoints = []
        self.caption_errors = []
        self.caption_warnings = []
        # What has played since the last break: a caption, and anything else.
        self.caption_since_break = False
        self.content_since_break = False
        self.helper_playing = False
        self.click_warnings = []

    def play(self, *animations, **kwargs):
        """Scale every run time by PACE, and in a dry run note any FadeOut that would play
        after other content without a break in between. Scene.wait() plays a Wait, so
        waits are scaled here too, and a wait alone shows nothing new."""
        prepared = [prepare_animation(animation) for animation in animations]
        if "run_time" in kwargs:
            kwargs["run_time"] = _whole_frames(kwargs["run_time"] * self.pace)
        else:
            for animation in prepared:
                animation.run_time = _whole_frames(animation.run_time * self.pace)
        if config["dry_run"] and not self.helper_playing and self.content_since_break:
            if any(_fades_out(animation) for animation in prepared):
                shown = getattr(self.caption, "text", None) or "(two-line caption)"
                self.click_warnings.append(f"FadeOut without a click, under caption {shown!r}")
        super().play(*prepared, **kwargs)
        if not self.helper_playing and not all(isinstance(a, Wait) for a in prepared):
            self.content_since_break = True

    @contextlib.contextmanager
    def rolling(self):
        """Animations that finish a placement (a block moving into its slot, a highlight
        clearing after it) roll through without a click, since they add to the picture
        rather than take words away. Use it only for that."""
        self.helper_playing = True
        try:
            yield
        finally:
            self.helper_playing = False
            self.content_since_break = True

    def mark(self, name, offset=0.0):
        self.checkpoints.append({"name": name, "time": round(float(self.time) + offset * self.pace, 3)})

    def pause(self, name, hold=None):
        """Hold for viewers of the continuous MP4, then end the slide here."""
        if hold is None:
            hold = self.read
            if self.cps and self.caption is not None:
                on_screen = float(self.time) - self.caption_shown_at
                hold = max(hold, (self.caption_chars / self.cps - on_screen) / self.pace)
        if hold:
            self.wait(hold)
        self.mark(f"break-{name}", offset=-0.1)
        self.next_slide()
        self.caption_since_break = False
        self.content_since_break = False

    def tear_down(self):
        destination = Path(os.environ.get("CHECKPOINT_DIR", "build/checkpoints"))
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / f"{type(self).__name__}.json"
        path.write_text(json.dumps(self.checkpoints, indent=2))
        for suffix, lines in (
            ("caption-errors", self.caption_errors),
            ("caption-warnings", self.caption_warnings),
            ("click-warnings", self.click_warnings),
        ):
            if lines:
                notes = destination / f"{type(self).__name__}.{suffix}"
                notes.write_text("".join(f"{type(self).__name__}: {line}\n" for line in lines))

    def title_card(self, number, title):
        """The part's opening card, which the click that starts the part also clears."""
        card = VGroup(
            label(f"Part {number}", size=30, color=MUTED),
            label(title, size=52),
        ).arrange(DOWN, buff=0.3)
        self.helper_playing = True
        self.play(FadeIn(card, shift=0.2 * UP), run_time=0.8)
        self.mark("title", offset=0.0)
        self.wait(1.2)
        self.play(FadeOut(card), run_time=0.5)
        self.helper_playing = False

    def say(self, text, hold=0.0):
        """Show a caption. Replacing one takes a click first if anything has played since
        the last break, so the presenter decides when the old words leave."""
        try:
            new = make_caption(text, max_width=self.caption_max_width)
        except ValueError as error:
            # render.sh check collects every caption defect in one pass instead of
            # stopping at the first; a real render still stops here.
            if not config["dry_run"]:
                raise
            self.caption_errors.append(str(error))
            new = label("(caption too wide)", size=CAPTION_SIZE).move_to([0, CAPTION_Y, 0])
        else:
            if config["dry_run"]:
                try:
                    make_caption(text, min_scale=1, max_width=self.caption_max_width)
                except ValueError:
                    self.caption_warnings.append(f"Caption shrinks to fit: {text!r}")
        if self.caption is not None and (self.caption_since_break or self.content_since_break):
            self.pause(f"before-caption-{len(self.checkpoints):02d}")
        self.helper_playing = True
        if self.caption is None:
            self.play(FadeIn(new, shift=0.15 * DOWN), run_time=0.6)
        else:
            self.play(
                FadeOut(self.caption, shift=0.15 * UP),
                FadeIn(new, shift=0.15 * UP),
                run_time=0.6,
            )
        self.helper_playing = False
        self.caption = new
        self.caption_chars = len(text)
        self.caption_shown_at = float(self.time)
        self.caption_since_break = True
        self.mark(f"caption-{len(self.checkpoints):02d}", offset=0.3)
        if hold:
            self.wait(hold)

    def clear_stage(self, run_time=0.6):
        """Fade out everything except the caption, after a click if anything has played
        since the last break."""
        others = [mob for mob in self.mobjects if mob is not self.caption]
        if not others:
            return
        if self.caption_since_break or self.content_since_break:
            self.pause(f"before-clear-{len(self.checkpoints):02d}")
        self.helper_playing = True
        self.play(*(FadeOut(mob) for mob in others), run_time=run_time)
        self.helper_playing = False
