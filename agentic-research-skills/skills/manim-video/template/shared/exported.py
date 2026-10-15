# Copied from <skills>/manim-video/template on __DATE__.
"""A research project's exported numbers, read so a video shows the values the paper shows.

    from exported import Numbers

    NUMBERS = Numbers(PROJECT / "results/latex/numbers.tex")
    NUMBERS.text("adjPoolATT")                 # "0.271", the string the paper typesets
    NUMBERS.check("adjPoolATT", att, places=3)  # asserts a recomputed value rounds to it

The files hold \\newcommand{\\name}{value} lines (also \\renewcommand, \\providecommand, and \\csdef),
parsed the way /research-deck's sources.py parses them. A video displays text() strings
directly, so a rerun of the project's pipeline changes the video on its next render. check()
covers values the video computes itself from exported tables (a plotted series, a bar
height), so a stale table and the paper cannot disagree silently.
"""

import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# etoolbox \csdef{name}{value} lines are read too, and their names may hold digits
# (thkZero1990N). Added 2026-10-12 for ob-generic-entry.
MACRO = re.compile(
    r"^\s*\\(?:(?:newcommand|renewcommand|providecommand)\{\\([A-Za-z]+)\}|csdef\{([A-Za-z0-9]+)\})"
    r"\{(.*)\}\s*(?:%.*)?$",
)


def latex_to_text(value):
    """Render a macro value as plain text (percent signs, separators, minus signs)."""
    text = (
        value.replace(r"\%", "%")
        .replace(r"\&", "&")
        .replace("{,}", ",")
        .replace(r"\,", "\u2009")
        .replace(r"\$", "$")
    )
    text = text.replace("$", "").replace("--", "\u2013")
    return re.sub(r"(^|[\s(])-(?=\d|\.\d)", "\\1\u2212", text)


def _half_up(value, places):
    return Decimal(repr(float(value))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


class Numbers:
    def __init__(self, *paths):
        self.paths = [Path(path) for path in paths]
        self.macros = {}
        for path in self.paths:
            for line in path.read_text().splitlines():
                match = MACRO.match(line)
                if match:
                    self.macros[match.group(1) or match.group(2)] = match.group(3)
        if not self.macros:
            raise ValueError(f"No macros found in {', '.join(map(str, self.paths))}")

    def text(self, name):
        if name not in self.macros:
            raise KeyError(f"\\{name} is not in {', '.join(map(str, self.paths))}")
        return latex_to_text(self.macros[name])

    def value(self, name):
        """The macro as a number, ignoring separators, a percent sign, and a Unicode minus."""
        text = self.text(name).replace(",", "").replace("%", "").replace("\u2212", "-").strip()
        return float(text)

    def check(self, name, computed, places):
        # Rounds half up, as projects that write macros with Decimal.quantize(ROUND_HALF_UP) do;
        # Python's round() sends 22.5 to 22 and fails a correct 23 (ob-generic-entry, 2026-10-12).
        shown = self.value(name)
        if _half_up(computed, places) != _half_up(shown, places):
            raise AssertionError(f"\\{name} is {shown}, but the video computes {computed:.{places + 2}f}")
