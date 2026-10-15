---
name: idea-grading
description: "Generates and ranks research ideas from the data a group has in hand. Writes a data inventory and a shared brief, runs several independent brainstorm passes on different models, merges near-duplicates with the owner's approval, has several models grade every idea blind against a fixed rubric, and combines the grades into a ranked list with the graders' disagreements shown. Use when the user wants research ideas from a set of data sets, wants a list of ideas graded or ranked, or asks which project to start next."
---

# idea-grading

The method runs in five stages, each a separate step with its own files, so a stage can be rerun
without repeating the ones before it:

1. **Inventory.** What data the group has, written down once.
2. **Brainstorm.** Several models propose ideas independently from the same brief.
3. **Merge.** Near-duplicates are combined, with the owner's approval.
4. **Grade.** Several models score every idea against a fixed rubric, without seeing each other.
5. **Rank.** The grades are combined into one list, and the owner picks what to start.

Using models from different vendors at stages 2 and 4 matters more than using many passes of one
model, because models from one family tend to propose and favor the same things. `<skills>` below
means the folder that holds this skill. The owner is the researcher whose program this is.

## Files

- `idea-schema.md`, the fields every idea carries.
- `rubric-template.md`, the five scored criteria with anchors. The owner edits the impact and fit
  anchors for their program.
- `scripts/combine_grades.py`, which ranks the graded ideas (Python standard library only).

The run lives in a folder of its own, e.g., `research-ideas/`, laid out as `inventory/`,
`brainstorm/`, `ideas/`, and `grading/`.

## 1. Inventory

Write `inventory/data-inventory.md` with the owner: one section per data set with its source,
coverage (period, places, units), size, key fields, how it links to the others, known traps, and
any results already established from it. Add a section on the group's prior papers and work in
progress. Ask the owner about anything the files do not say. Every later stage reads this file and
nothing else about the data, so a gap here becomes a gap in every idea. Never put row-level
identifiers (names, phone numbers, user ids) in it.

## 2. Brainstorm

1. Write `brainstorm/brief.md`: the program and its audience, what is asked (every substantive idea
   the data could support, in any discipline, now or with a named addition such as new data,
   annotation, or ethics review), the rules (cite the inventory for every fact about the data, never
   invent a number, mark unverified literature), the output format (a JSON array of ideas in the
   shape of `idea-schema.md`), and, when ideas are already on file, their titles, with the
   instruction not to resubmit one unchanged.
2. Ask the owner which models run the passes. Three passes on three models is a good default
   (e.g., Opus and Fable in Claude Code, and Codex).
3. Give every pass the same brief, independently and in parallel. Ways to run a pass: a subagent in
   Claude Code, `codex exec` with the brief as its prompt, or any chat model with the brief and the
   inventory attached. Save each pass's output verbatim as `brainstorm/<model>.json`.
4. Check each file parses and has every schema field. Do not edit a pass's ideas.

## 3. Merge

Read every title, then compare the research questions within each group of similar titles. Propose
merge groups to the owner, each with its reason, and list the near-matches you kept apart and why.
After the owner approves, write `ideas/merged.json` with a stable id per idea (`I001`, `I002`, ...)
and, for each merged idea, the sources and models that proposed it. Keep the raw pass files
unchanged.

## 4. Grade

1. Copy `rubric-template.md` to `grading/rubric.md`, and have the owner finish the impact and fit
   anchors.
2. Write `grading/titles.md` (every id and title) and split the ideas into packets of about 25 to
   100, so each grader can finish a packet in one sitting.
3. Write `grading/instructions.md`: read the rubric, read the inventory (ability to execute must
   reflect what the inventory says is in hand, not what the idea claims), read every title before
   scoring anything so the scale stays consistent, then grade the packet in order. Names of models
   inside an idea's text are not a reason to score it up or down.
4. Ask the owner which models grade. Use at least three graders from at least two vendors, and
   never tell a grader what another gave.
5. Run every grader over every packet, in parallel, and save the raw outputs. Combine each grader's
   packets into `grading/<grader>.json`.
6. Check that every grader file holds every id exactly once, with integer scores from 1 to 5.

## 5. Rank

Run `python <skills>/idea-grading/scripts/combine_grades.py grading/*.json --ideas ideas/merged.json
--out grading/ranked.md`. It ranks ideas by mean total score (the five criteria summed, averaged
over graders), shows each criterion's mean, and flags ideas where the graders' totals differ by 5
or more, since those are the ideas worth reading closely rather than trusting the mean.

Show the owner the top of the list and the flagged disagreements. The owner picks what to start.
For each pick, write a one-page brief from the idea's record (questions, data, method, plan,
risks) to start the project with, and record the pick in `ideas/projects.json` (id, stage, date,
and where the project lives) so the list shows which ideas are under way.

## Never

- Never let a grader see another grader's scores or the brainstorm pass an idea came from.
- Never change a score by hand. Rerun the grader instead.
- Never present the ranking as the decision. It is input to the owner's choice.
