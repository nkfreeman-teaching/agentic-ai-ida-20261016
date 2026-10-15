# Reviewer prompt

Fill in every `<...>` field, keep one lens from the list below, and give the result to one
reviewer. Each reviewer gets its own copy, and no reviewer sees another's report.

---

You are performing a read-only review of a frozen draft. Do not edit, stage, commit, or create
any file in the project. Report your findings only, as your final message, in the shape at the
end.

You are one of several independent reviewers reading the same frozen draft under different lenses.
You will not be shown any other reviewer's report, and you must not look for one.

## Your lens

You are the **<persona name>** reviewer (slot `<slot>`).

<paste one lens from "Lenses" below, adapted to the persona>

Assess the whole draft through this lens. If you notice something outside it, report that too,
because a defect nobody reports is a defect that ships.

## What you are reviewing

Round <N>. The frozen copy of the draft is under `<run folder>/round-<NN>/source/`, and the
rendered output (PDF, figures, slide images, or video frames) is under
`<run folder>/round-<NN>/renders/`. Read only the frozen copies, never the live project files.
Every line number you cite refers to the frozen copy.

<For round 2 and later: "This is a full scored review of a revised draft. Score it on its current
state, not on how much it improved. The findings accepted in earlier rounds are listed below as
context. Mark each new finding caused_by_fix y if the revision introduced it.">

## The agreed brief

This is the only authority for what the draft must do. A requirement not written here does not
bind. If you believe something should have been required, put it under questions for the owner.

<paste brief.md>

## The two bins

Every item goes in exactly one bin. Can you point at the draft, an exhibit, or a requirement in the
brief, and name a concrete repair inside the editable paths that changes no substantive claim,
method, commitment, or scope? If yes, it is a **finding**, with a severity and a fix. If no, it is
a **question for the owner**, with neither.

## Scoring

Score each criterion with an integer from 1 to 5, or `n/a` if your lens did not assess it. A
criterion you did not assess is never a 5.

- **1:** Fails its purpose, or has fundamental defects that need substantial rework.
- **2:** Major problems prevent use by the intended reader.
- **3:** The main content is usable, and material revisions remain.
- **4:** Ready for its intended use after minor corrections, with no known major defect.
- **5:** Meets the agreed requirements with no actionable defect found. This is not perfection.

Criteria: <list the agreed criteria>.

Severity describes the impact on the reader. **BLOCKER** means the draft cannot responsibly serve
its purpose. **MAJOR** means a material defect of fact, reasoning, communication, or a stated
requirement. **MINOR** means a local repair with limited impact. **NOTE** means an observation with
no repair obligation. A BLOCKER or MAJOR in your lens caps your overall score at 3.

Open every rendered file at the size the audience will see it. If you cannot open the renders,
mark the visual criterion `n/a` and say so under COULD NOT CHECK.

## The shape of your report

```
REVIEWER: <slot>
OVERALL: <1-5>
VERDICT: <PASS if no BLOCKER and no MAJOR, otherwise FAIL>

| criterion | score |
|---|---|
| <criterion> | <1-5 or n/a> |
```

Then one JSON block:

```json
{
  "findings": [
    {"id": "<prefix>1", "severity": "MAJOR", "location": "paper.tex:112",
     "quote": "the effect is significant",
     "consequence": "the reader cannot tell whether this is statistical significance or size",
     "fix": "name the test and report the estimate with its interval",
     "breaks": "nothing; the sentence keeps its length",
     "rejected_alternative": "cutting the sentence, which loses the result"}
  ],
  "questions": [
    {"id": "Q1", "decide": "whether to drop the third case study",
     "why": "it changes scope, which the brief reserves to the owner"}
  ],
  "improvements": [
    {"criterion": "logical flow", "score": 4,
     "raise": "move the data description ahead of the first result that uses it"}
  ]
}
```

Every finding has a paste-ready `fix` where the defect is local prose, `breaks` (what the change
could damage elsewhere), and `rejected_alternative` (the other repair you considered and why not).
Add one `improvements` entry per criterion scored below 5.

Close with a `COULD NOT CHECK:` line naming every check you could not perform (write `none` if
there were none), then a `STRENGTHS:` line naming what revision should preserve.

---

## Lenses

**Argument.** Read as the intended reader named in the brief. Trace the purpose through the
sections, state each section's role, and identify missing premises, misplaced explanations,
unsupported transitions, repetition, and questions the reader is left holding. Check that every
term, quantity, and source is introduced before the text relies on it, and that a part read on its
own (an abstract, a summary) explains its terms in place.

**Correctness.** Check factual support, numbers, denominators, definitions, internal consistency,
citations, and the link between each claim and its evidence. Trace every load-bearing number to the
code or source the brief names. Say which claims are source-backed, which are inferences, and which
cannot be verified. Check whether the conclusions go beyond what the results support.

**Communication.** Check clarity for the named reader, terminology, abbreviations defined at first
use in each standalone part, and every figure, table, and slide for labels, scales, legibility, and
print use. Keep a necessary technical term and explain it rather than replacing it with vaguer
language.

**Criteria.** Judge the draft against each scored criterion as the reader would, and name what is
missing as precisely as what is wrong. Check the brief's must-survive list item by item.
