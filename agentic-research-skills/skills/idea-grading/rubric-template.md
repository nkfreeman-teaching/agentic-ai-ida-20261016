# Grading rubric

Score every idea on five criteria, each an integer from 1 to 5. Use the anchors below, and use 2
and 4 for ideas that fall between anchors. Score each idea as written, and do not reward or
penalize an idea for its length, polish, or who might have proposed it. Grade against the anchors,
not against the other ideas, but read every title before scoring anything so the scale stays
consistent from the first idea to the last.

The owner fills in the parts marked _TBD_ before grading starts.

## 1. `execute`: ability to execute with the available data

- **5.** Every data set the idea needs is in hand (see the data inventory), any linkage it relies
  on already exists, and a first check is a few days of work.
- **3.** The core data are in hand, but the idea needs one substantial addition, i.e., new data, an
  annotation effort, an open-data download and linkage, or an ethics review.
- **1.** The idea depends on data the group does not have and cannot plausibly get, or an earlier
  attempt failed for a reason the idea does not address.

## 2. `impact`: importance of the questions

- **5.** Answering it would change what _TBD (the practitioners or decision makers the program
  serves)_ do, or settle a first-order open question in the field.
- **3.** Useful knowledge for one research community or one practitioner group, with incremental
  consequences.
- **1.** Mostly of curiosity value, with little consequence either way.

## 3. `publication`: expected potential for publication

- **5.** A clear new contribution with a design that reviewers at a top journal in at least one
  field would accept (e.g., _TBD: the top venues for this program_).
- **3.** A solid paper for a good field journal, or a top-venue paper with a real design weakness
  to overcome.
- **1.** Hard to publish anywhere reputable, because it is descriptive only, crowded, or its design
  cannot support its claim.

## 4. `risk`: how manageable the limitations and risks are

Higher is better. Consider identification threats, measurement validity, data access and
licensing, ethical exposure (harm to people in the data, re-identification, misuse of results),
ethics review burden, and legal exposure.

- **5.** Limitations are minor and standard, with obvious mitigations.
- **3.** Notable limitations that known methods or extra data can address, at real cost.
- **1.** Severe risks with no clear mitigation, i.e., a claim the data cannot support, serious harm
  potential, or access that may be legally or contractually impossible.

## 5. `fit`: fit with the research program

The program is _TBD (one or two sentences describing it)_.

- **5.** Central to the program and builds on the group's data or prior papers.
- **3.** Adjacent to the program, or a methods contribution the program would use.
- **1.** Unrelated to the program.

## Text fields

- `communities`: the one to three scholarly communities most likely to care.
- `venues`: two or three specific journals or conferences, most likely first.
- `largest_risk`: the single most serious risk or limitation, in one sentence.
- `rationale`: one or two sentences explaining the scores.

## Output

A JSON array with one object per idea:

```json
{"id": "I001", "execute": 4, "impact": 5, "publication": 4, "risk": 3, "fit": 5,
 "communities": ["operations management", "public health"],
 "venues": ["Management Science", "Health Affairs"],
 "largest_risk": "...", "rationale": "..."}
```
