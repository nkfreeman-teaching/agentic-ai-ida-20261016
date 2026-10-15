"""Rank graded research ideas by their mean total score across graders.

    python combine_grades.py grading/opus.json grading/fable.json grading/codex.json \
        --ideas ideas/merged.json --out grading/ranked.md

Each grader file is a JSON array of objects with an "id" and an integer from 1 to 5 for each
criterion. The total is the criteria summed (out of 25 with five criteria), and the mean total is
averaged over graders. Ranks are competition ranks, so tied ideas share a rank. An idea whose
graders' totals differ by --spread or more is flagged, since its mean hides a disagreement worth
reading. Standard library only.
"""

import argparse
import json
from pathlib import Path

CRITERIA = ("execute", "impact", "publication", "risk", "fit")


def load_grades(paths):
    grades = {}
    for path in paths:
        rows = json.loads(Path(path).read_text())
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise SystemExit(f"{path}: an id appears more than once")
        for row in rows:
            for criterion in CRITERIA:
                if row.get(criterion) not in (1, 2, 3, 4, 5):
                    raise SystemExit(f"{path}: {row['id']} has {criterion}={row.get(criterion)!r}")
        grades[Path(path).stem] = {row["id"]: row for row in rows}
    id_sets = {grader: set(rows) for grader, rows in grades.items()}
    first = next(iter(id_sets.values()))
    for grader, ids in id_sets.items():
        if ids != first:
            raise SystemExit(f"{grader} grades a different set of ideas ({len(ids)} against {len(first)})")
    return grades


def rank(grades):
    graders = list(grades)
    ideas = sorted(next(iter(grades.values())))
    table = []
    for idea in ideas:
        totals = [sum(grades[g][idea][c] for c in CRITERIA) for g in graders]
        table.append(
            {
                "id": idea,
                "mean_total": sum(totals) / len(totals),
                "totals": dict(zip(graders, totals, strict=True)),
                "spread": max(totals) - min(totals),
                "criteria": {
                    c: sum(grades[g][idea][c] for g in graders) / len(graders) for c in CRITERIA
                },
            },
        )
    for row in table:
        row["rank"] = 1 + sum(1 for other in table if other["mean_total"] > row["mean_total"])
    return sorted(table, key=lambda row: (row["rank"], row["id"]))


def write_markdown(table, titles, out, spread):
    graders = list(table[0]["totals"])
    lines = [
        "# Ranked ideas",
        "",
        f"{len(table)} ideas, {len(graders)} graders ({', '.join(graders)}). Mean total is out of "
        f"{5 * len(CRITERIA)}. A flag marks graders' totals that differ by {spread} or more.",
        "",
        "| rank | id | title | mean total | " + " | ".join(CRITERIA) + " | " + " | ".join(graders) + " | flag |",
        "|" + "---|" * (5 + len(CRITERIA) + len(graders)),
    ]
    for row in table:
        cells = [
            str(row["rank"]),
            row["id"],
            titles.get(row["id"], ""),
            f"{row['mean_total']:.2f}",
            *(f"{row['criteria'][c]:.1f}" for c in CRITERIA),
            *(str(row["totals"][g]) for g in graders),
            "disagree" if row["spread"] >= spread else "",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    Path(out).write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("graders", nargs="+", help="one JSON file per grader")
    parser.add_argument("--ideas", help="merged ideas file; titles are matched by id, or by position as I001, I002, ...")
    parser.add_argument("--out", default="ranked.md")
    parser.add_argument("--spread", type=int, default=5)
    args = parser.parse_args()

    grades = load_grades(args.graders)
    titles = {}
    if args.ideas:
        for i, idea in enumerate(json.loads(Path(args.ideas).read_text()), start=1):
            titles[idea.get("id", f"I{i:03d}")] = idea["title"]
    table = rank(grades)
    write_markdown(table, titles, args.out, args.spread)
    flagged = sum(1 for row in table if row["spread"] >= args.spread)
    print(f"Ranked {len(table)} ideas from {len(grades)} graders into {args.out}; {flagged} flagged.")


if __name__ == "__main__":
    main()
