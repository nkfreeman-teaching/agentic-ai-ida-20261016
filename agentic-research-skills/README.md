# Agentic research skills

This folder holds the four skills behind the research pipeline we used in the week of October 11,
2026, plus a starter file of working preferences. A skill is a plain text file (`SKILL.md`) that
describes a procedure, which a coding agent reads when a task matches it. Because each skill is
plain text, the same files work with Claude Code, Codex, or any agent that can read files and run
commands.

## The pipeline

The skills follow the stages of one project, from an idea to a short video of its result:

1. **Ideas and grades** (`skills/idea-grading/`). Several models propose research ideas from a
   written inventory of the data on hand, and several models grade every idea against a fixed
   rubric (ability to execute, impact, publication potential, risk, and fit). In our run, three
   models proposed 121 new ideas, which merged with 184 already on file into 281, and three graders
   scored all 281.
2. **Checking the analysis** (`skills/adversarial-review/`). Before computing, the researcher
   writes down a rule for when the project continues or stops. One agent runs the analysis, and a
   model from another vendor tries to break it, returning findings that each carry a proposed fix.
3. **The writing loop** (`skills/review-loop/`). A frozen copy of the draft goes to several blind
   reviewers, each playing a set role (e.g., a journal referee or a correctness checker), who score
   it and return findings with fixes. The agent verifies each finding, applies the accepted fixes,
   and repeats until the score levels off or a round limit is reached.
4. **The video** (`skills/manim-video/`). An animated explainer built with Manim (a Python animation
   library) renders as a continuous MP4 and as a click-through deck, with every number on screen
   checked against the paper's exported results.

The decisions between stages (which ideas to start, whether a result clears its stop rule, and
whether a draft is ready) stay with the researcher.

## Installing the skills

- **Claude Code.** Copy each folder under `skills/` into `~/.claude/skills/` (for every project) or
  into a project's `.claude/skills/` (for one project). Claude Code lists them and loads one when a
  request matches its description, or when it is named, e.g., `/review-loop`.
- **Codex.** Recent versions of Codex read skills from `~/.codex/skills/`, so copy the folders
  there. With an older version, name the file in the prompt, e.g., "Read
  skills/review-loop/SKILL.md and follow it for this draft."
- **Any other agent.** Point it at the `SKILL.md` file in the prompt, as above.

`AGENTS.md` is the starter preferences file. Codex reads `AGENTS.md`, and Claude Code reads the
same content saved as `CLAUDE.md`. Each skill's `SKILL.md` lists anything it needs beyond the agent
itself (e.g., the video skill needs pixi and one font).

## Getting started

The most useful first step is a project whose data we already know well, so that each stage's
output can be judged on sight. Three habits made the most difference in our week. First, state the
vision: a long prompt (often dictated by voice) that gives the goal, the reasons, what to read, and
which decisions to ask about works better than a series of one-line instructions. Second, add a
second model as a critic, and require a proposed fix with every finding. Finally, keep the
decisions with the researcher, including stop rules written down before the result is computed.

These files were adapted from working versions on one machine. Paths, tool names, and commands may
need small changes on another setup, and the agent can usually make them when asked.
