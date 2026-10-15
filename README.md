# Agentic research workflows

This repository holds the deck and the agent skills from "Agentic research workflows," an informal session for Institute of Data and Analytics (IDA) staff and faculty on October 16, 2026, in 240 Bidgood Hall. The session described a workflow for generating, testing, and drafting research ideas with coding agents (Claude Code and Codex), and the skills folder holds the written procedure behind each stage of that workflow.

## Deck

The [deck](slides/research-workflow/research-workflow.html) ([PDF](slides/research-workflow/research-workflow.pdf)) is one self-contained HTML file that works offline. GitHub displays HTML files as source code, so to view the deck as slides, download the repository and open the file in a browser. Arrow keys or the space bar advance the slides, `T` switches between the light and dark themes, `F` enters full screen, and `?` lists the remaining keys. The speaker notes used in the session are not included in this copy.

The deck's source is `slides/research-workflow/src/deck.html`. `build.py` (Python standard library only) inlines the fonts, the logo, and the chart data into the HTML file, and `render.py` (which needs Playwright and Chrome) writes a PNG of each slide and exports the PDF. The score chart on the writing-loop slide reads `data/loops.json`, which holds the mean reviewer score by round for five review-loop runs from October 2026.

## Skills

`agentic-research-skills/` holds the four skills behind the workflow (`idea-grading`, `adversarial-review`, `review-loop`, and `manim-video`) and a starter preferences file (`AGENTS.md`). A skill is a plain text file that describes a procedure, which a coding agent reads when a task matches it, so the same folder works with Claude Code, Codex, or any agent that can read files and run commands. The folder's [README](agentic-research-skills/README.md) describes each stage and explains how to install the skills for each agent.

## Quoted sources

The deck quotes four posts on X. X blocks automated retrieval, so the wording of each quote was checked against copies of the post, and each date comes from the post's status ID.

- Andrej Karpathy, January 26, 2026, on success criteria ([post](https://x.com/karpathy/status/2015883857489522876)).
- Boris Cherny, January 2, 2026, on giving Claude a way to verify its work ([thread](https://x.com/bcherny/status/2007179832300581177)), quoted as reproduced at [paddo.dev](https://paddo.dev/blog/how-boris-uses-claude-code).
- Andrej Karpathy, July 21, 2026, on a long ramble session ([post](https://x.com/karpathy/status/2079610838143623371)).
- Boris Cherny, March 29, 2026, on coding by speaking to Claude ([post](https://x.com/bcherny/status/2038454362226467112), also on [Threads](https://www.threads.com/@boris_cherny/post/DWfjweulFcH)).
