# ML paper-writing method attribution

This Skill adapts the independently MIT-licensed Orchestra Research `ml-paper-writing` material at revision `773a52944ba4747a18bd4ae9ade53fff041adcbc`:

- Repository: <https://github.com/Orchestra-Research/AI-Research-SKILLs>
- Original directory: `20-ml-paper-writing/ml-paper-writing/`
- Original files read and adapted: `SKILL.md`, `references/checklists.md`, `references/reviewer-guidelines.md`. The citation workflow, writing guide, drafting checklist and venue/template handling were already adapted into the general [paper-drafting](../../paper-drafting/SKILL.md) Skill and are reused from there instead of duplicated; `references/writing-guide.md`, `references/citation-workflow.md` and `references/sources.md` were read to confirm that split.
- Copyright (c) 2025 Claude AI Research Skills Contributors. Full MIT terms accompany this Skill in `../LICENSE`.

The ML/AI professional method is retained at body level and bounded:

- Experiment reporting in `references/experiment-reporting.md` keeps the upstream Experiment/Reproducibility/Statistical-Significance/Compute/Limitations demands (error bars with a named method, number of runs/seeds, hyperparameter search ranges and selection, compute worker type/time/total, ablations, negative results, dedicated Limitations). Upstream illustrative numbers, default "3 seeds" style examples and environment setup are not turned into values; missing facts become visible gaps.
- `references/venue-checklists.md` keeps the full checklist structure (NeurIPS 16-item shape, ICML Broader Impact and reproducibility checklist, ICLR LLM disclosure, ACL mandatory Limitations and responsible-NLP items, universal pre-submission list). Year-specific page limits, deadlines and policy wordings become "verify the current official edition"; no conference template, style file, `.bib`/`.bst` or example PDF is vendored.
- `references/reviewer-expectations.md` keeps the four assessment dimensions, scoring calibration idea, common-concern/pre-emption tables and pre-submission reviewer simulation. Upstream's reading-rate percentages are removed as unverified; scoring labels are marked as edition-specific. Rebuttal handling stays with the separate user-invoked `rebuttal` entry.

No external paper, blog, conference template, style file or third-party image is vendored. The upstream `templates/` directory was inspected but not copied: it contains third-party LPPL bibliography/style packages, `natbib.sty` redistribution conditions not covered by the repository MIT license, and community templates with download/delete actions. The Skills that use a template require the user's own copy and license check.

## Method attribution

| Source | Author | Method attribution |
|---|---|---|
| [Highly Opinionated Advice on How to Write ML Papers](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) | Neel Nanda | Narrative, What/Why/So What, prioritizing reader entry points |
| [How to Write ML Papers](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) | Sebastian Farquhar | Five-part abstract and structure |
| [Heuristics for Scientific Writing](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) | Zachary Lipton | Precise wording and unnecessary intensifiers |
| [Advice for Authors](https://jsteinhardt.stat.berkeley.edu/blog/advice-for-authors) | Jacob Steinhardt | Precision and consistent terminology |
| [Easy Paper Writing Tips](https://ethanperez.net/easy-paper-writing-tips/) | Ethan Perez | Micro-level clarity and paragraph construction |
| [The Science of Scientific Writing](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) | George Gopen and Judith Swan | Reader expectations, topic/stress position and seven principles |

These links retain method attribution; they are optional background, not runtime dependencies, current venue rules, or citations to insert automatically into the user's paper.

## Official information

For a specified venue, locate the current edition's official author instructions, checklist and style files from the venue's own site, and record the URL and access date. Historical URLs, quotas and API snippets are not cached as current operational instructions.
