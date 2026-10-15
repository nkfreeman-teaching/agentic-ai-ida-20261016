---
name: review-loop
description: "Runs a bounded, scored review and revision loop over a frozen draft (a manuscript, proposal, white paper, memo, slide deck, or video frames). Interviews the owner into an agreed brief, agrees the rounds, reviewer personas, scored criteria, and a stopping rule, then freezes each round, dispatches blind reviewers (other models or subagents) who return scores and findings with fixes, verifies and applies the accepted fixes, and names the best round. Use when the user asks for a review loop, a writing loop, or scored rounds of independent review."
---

# review-loop

One draft, one agreed brief, one frozen copy per round, blind reviewers, then the owner. The loop
exists to make four things true: a score always names the exact text that earned it, no reviewer
sees another reviewer's findings, the draft cannot change while reviewers are reading it, and a
reviewer report is never written by the agent that dispatched it.

`<skills>` below means the folder that holds this skill. The owner is the person who owns the
draft.

## Files

- `brief-template.md`, the brief every reviewer receives. It is the only authority.
- `reviewer-prompt.md`, the prompt each reviewer receives, with the lenses, the scoring anchors,
  and the report shape.

## The contract

1. **The brief is the only authority.** Reviewers receive the brief and the frozen copy. A
   requirement not written in the brief does not bind. A decision recorded under "Settled
   decisions" is judged, not re-derived.
2. **Two bins.** A **finding** points at the draft, names a repair inside the editable paths, and
   carries a severity (BLOCKER, MAJOR, MINOR, NOTE) and a proposed fix. A **question for the
   owner** is anything whose repair would change a claim, a method, a commitment, or scope. It
   carries no severity and goes to the owner.
3. **A score belongs to its frozen copy.** Never carry a round's scores to a revised draft.
4. **Rounds to the cap, then the owner.** The loop never extends itself past the agreed cap.
5. **Authority is bounded.** The loop revises only the editable paths. It never sends, publishes,
   commits, pushes, deletes tracked files, or changes raw data.

## Start a run

1. **Read before asking.** Read the draft, the project's own instructions, and its evidence (the
   code and data that produce its numbers).
2. **Research the venue** when the draft is headed to one: its review criteria and the profile of
   its typical reviewers. The reviewer personas and criteria come from this.
3. **Interview the owner** in one or two batches of questions, each with your recommendation. Agree
   the shape of the loop:
   - the reviewer slots, each a persona with a lens (e.g., a journal referee reading for the
     argument, a methods referee, a domain expert or practitioner, and a correctness reviewer
     who traces every number to its producing code);
   - which model runs each slot (use at least two model families; a second vendor's model, such
     as Codex, catches different things);
   - the scored criteria (four to six, e.g., contribution, correctness, logical flow, clarity for
     the reader, exhibits);
   - the round cap (three is the default) and the stopping rule (stop when the round score gains
     less than 0.10 over the previous round, or at the cap).
4. **Open the run folder** at `review-loop/<date>-<topic>/` in the project, with `brief.md` copied
   from `brief-template.md` and filled in, and a `progress.md` holding a rounds table and a
   dispositions table.
5. **Build the renders.** Reviewers inspect rendered output (the compiled PDF, the figures, slide
   images, or video frames), never source alone.

## Run one round

1. **Freeze.** Copy every reviewed file and render into `round-NN/source/` and `round-NN/renders/`,
   and record a checksum of each (`sha256sum` or equivalent) in `round-NN/manifest.txt`.
2. **Write one prompt per slot** from `reviewer-prompt.md`: fill in the slot's lens, the frozen
   paths, the brief, and the criteria. Each prompt is self-contained, because a reviewer from
   another vendor has none of this machine's context.
3. **Dispatch every slot blind, in parallel, before touching anything.** Ways to run a slot:
   - Claude Code: a subagent (the Agent tool) with the prompt.
   - Codex: `codex exec` with the prompt file, in a read-only sandbox.
   - Any other agent or chat model: paste the prompt and attach the frozen files.
   Save each report verbatim as `round-NN/<slot>.md`. Edit nothing in the draft until every slot
   has reported. Never write or edit a reviewer report by hand, and never fill a missing slot with
   your own review.
4. **Tally.** Compute the round score as the mean of every scored criterion across reviewers.
   Count findings by severity. Record the round in `progress.md`.
5. **Adjudicate.** Verify every finding against the draft, the sources, and the renders, and
   record a disposition (accepted, rejected, or deferred) with the reason. Where two reviewers
   disagree, record both positions and take the higher severity. Group findings by root cause. Ask
   the owner about every BLOCKER or MAJOR you reject or downgrade and every question for the
   owner, in one batch.
6. **Fix and rebuild.** Apply accepted fixes only. Regenerate every dependent output by rerunning
   the code that writes it, never by hand-editing a generated number or figure. Look at the rebuilt
   renders, since a fix that introduces a defect is how later rounds score lower.
7. **Next round** while the stopping rule says continue.
8. **Stop and hand back.** Report the score by round, the best round, each open BLOCKER or MAJOR,
   the unanswered questions for the owner, and the checks that could not be performed. If an
   earlier round scored highest, say so and offer to restore its frozen copy. Do not extend the
   loop to chase a higher score; in past runs, a round past the plateau usually scored lower.

A cap, a plateau, or an unresolved major defect is a stopping reason, not evidence of success. Say
which one stopped the loop.

## Never

- Never edit the draft while reviewers are reading it.
- Never show one reviewer another reviewer's report.
- Never accept a finding without checking it against the files.
- Never record an exhibit, slide, or frame as passed without looking at it.
