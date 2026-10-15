# Idea schema

Every idea, whether already on file or newly proposed, is one JSON object with these keys. A
brainstorm pass returns a JSON array of them.

| Key | Type | Content |
|---|---|---|
| `title` | string | Short descriptive title, sentence case. |
| `domain` | string | A short label the owner chooses for the data group or field (e.g., `labor`, `methods`, `linkage` for ideas that join several sources). |
| `relation` | string | `new`, or `extends: <existing title>`, `combines: <titles>`, or `revives: <title> (what the earlier attempt missed)`. |
| `research_questions` | list of strings | One to four concrete questions. |
| `why_it_matters` | string | Who benefits (researchers, practitioners, policy) and what changes if the questions are answered. |
| `data_needed` | string | Data sets and fields, citing the inventory. Flag plainly anything not in hand, i.e., new collection, annotation, ethics review, or open data to download. |
| `method_sketch` | string | Design, estimator, or model, with the identification strategy if the claim is causal. |
| `plan` | list of strings | Three to six steps from first check to submission. |
| `prior_evidence` | string | Inventory facts or earlier results the idea builds on, with their source, or "none". |
| `risks` | string | Data, identification, ethical, and publication risks, each with a possible mitigation. |
| `candidate_venues` | list of strings | Journals or conferences, most likely first. |
| `source` | string | The model or file that proposed the idea. |

After merging, each idea also carries `id` (e.g., `I001`) and `proposers` (every pass that proposed
it).
