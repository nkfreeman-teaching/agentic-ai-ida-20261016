---
name: adversarial-review
description: "Checks a data analysis before anyone writes it up. The owner fixes a stop rule before the result exists, one agent runs the analysis, and a second model from another vendor tries to break it, returning findings that each carry a proposed fix; the analyst verifies every finding before applying it and records each disposition. Use when the user asks for an adversarial review, a critic pass, a second model's check of an analysis, or a stop rule (kill test) for a new project."
---

# adversarial-review

An agent that runs an analysis is a poor judge of it, because it reads its own code with the
intentions it wrote it with. This skill splits the work: an **analyst** builds the analysis, a
**critic** from a different model family tries to break it, and the **owner** (the researcher)
makes every decision that changes a claim, a method, or scope. `<skills>` below means the folder
that holds this skill.

Everything is recorded in the project's `DECISIONS.md`: one entry per load-bearing choice, with its
reason and the alternative rejected, edited in place when a decision changes.

## 1. Fix the stop rule before computing

Before the headline number exists, agree with the owner and write in `DECISIONS.md`:

- **The question and the estimate** that answers it, in one or two sentences, with its units and
  denominator.
- **The checks** the result must survive (e.g., another dating rule, dropping the largest units,
  another source or snapshot).
- **The rule**: the value at or above which the project continues, the value below which it stops,
  and what happens in between (it goes back to the owner). The rule names whether every check must
  pass or only the main estimate.
- The date, and the words "fixed before computing". A rule written after the number was seen is
  labeled post hoc.

For example, a study of a rise in some count might continue only if the count at least doubles
under every check, while a study of a growth rate might continue at 20% or more, stop below 10%,
and return to the owner in between.

## 2. Build the analysis

The analyst writes the pipeline as numbered stages, each a script that reads saved inputs and
writes saved outputs, so any stage can be rerun alone. Every number that will appear in a paper is
written by code to an exported numbers file (e.g., LaTeX macros or a JSON file), never typed. Each
run logs to a dated file with its exit code. After every join, filter, or aggregation, print and
keep the row counts before and after.

Run the stop rule as its own script, which prints the verdict and exits nonzero on STOP.

## 3. Send the analysis to the critic

The critic is a model from another vendor than the analyst's (e.g., Codex when the analyst is
Claude, or the reverse). Write `review/critic-brief.md` from the template below, and run it
read-only:

- Codex: `codex exec --sandbox read-only "$(cat review/critic-brief.md)"`, saving the final message
  to `review/critic-<date>.md`.
- Claude Code: a subagent with the brief as its prompt.
- Any chat model: paste the brief and attach the files it names.

The critic may rerun the pipeline only in a copy of the project, never in the project itself.

### Critic brief template

```
You are reviewing a data analysis before it is written up. Your job is to find what is wrong
with it. Do not edit any file in the project. If you need to rerun anything, work in a copy.

The question and the stop rule: see DECISIONS.md, sections <...>.
The code: scripts/<...>, run in the order <...>. The saved outputs: data/derived/<...>.
The latest run log: logs/<...>.

Look for, at least: wrong joins (rows multiplied or lost), wrong denominators, filters that
remove more or other rows than intended, double counting, units or dates mixed up, stale inputs,
results that depend on an arbitrary threshold, a stop rule implemented differently from how it
is written, and any claim in the notes that goes beyond what the outputs show.

Return every finding, whatever its size, as a numbered list (F01, F02, ...). For each give:
severity (BLOCKER, MAJOR, MINOR, NOTE); location (file and line, or output and column);
evidence (what you observed, with a command or query that reproduces it); the proposed fix (the
specific change and where it goes); what the fix could break; and the alternative fix you
considered and rejected, with the reason. Put anything that would change the question, the
method, or the scope under a separate heading, Questions for the owner.
```

Do not set a severity floor in the brief. Ask for every finding and filter afterward.

## 4. Verify, decide, and record

For each finding:

1. **Verify it** against the code and data by reproducing the evidence. A finding that does not
   reproduce is rejected, with what you ran.
2. **Decide**: accepted (and applied), rejected (with the reason), or deferred (with what it
   needs). Anything that changes a claim, a method, or scope goes to the owner.
3. **Record** it in `DECISIONS.md`, naming the finding it closes (e.g., "(F10)"). Where the
   analyst and the critic disagree on a finding or its severity, record both positions and take
   the higher severity.

Then rerun the whole pipeline from its first stage, rerun the stop rule, and report its verdict
with the log's exit code. If the fixes were substantial, send the changed parts back to the critic
for one more pass.

## 5. Apply the rule

- **Continue**: the project moves to drafting.
- **Stop**: report the result and why it stopped. A stopped project is a result, not a failure.
- **In between**: the owner decides, with the evidence laid out. Options include stopping,
  narrowing the claim to what the result supports, or reframing the question. Record the decision
  and the alternatives rejected.

## Never

- Never change the stop rule after seeing the result without labeling the new rule post hoc.
- Never apply a finding without verifying it, and never reject one without saying what you ran.
- Never let the critic edit the project.
- Never type a number into a draft that the code did not export.
