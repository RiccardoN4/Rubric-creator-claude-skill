# rubric-creator

`rubric-creator` is a Claude Code skill that generates a `rubric.json` in the exact PaperBench format from a machine learning paper folder containing a PDF and, optionally, a pre-extracted `paper.md`, addendum, or notes.

The skill is built as a checkpointed multi-pass pipeline rather than a one-shot prompt. It analyzes the paper, constructs the rubric top-down, reviews coverage, validates the result programmatically, and iterates until the rubric is structurally compliant with the PaperBench format.

## What this repository contains

This repository is the skill bundle itself.

Main files:
- `SKILL.md`: the operational procedure Claude Code follows
- `validate_rubric.py`: the validator used in the repair loop
- `reference/structural_principles_complete.md`: quantitative structural priors extracted from the benchmark
- `reference/rubric_schema_reference.md`: code-level schema rules and compatibility constraints
- `reference/rubric_schema.json`: formal JSON Schema for a valid rubric
- `reference/annotated_examples/`: five annotated PaperBench rubric examples spanning small, typical, result-heavy, execution-heavy, and very large cases

## What the skill does

Given a paper directory, the skill:
1. reads `paper.md` if present, otherwise extracts text from the paper PDF
2. writes `paper_analysis.md` with contributions, experiments, datasets, baselines, metrics, dependencies, and complexity estimate
3. generates `rubric.json` top-down using PaperBench structural priors
4. writes `coverage_review.md` to identify missing contributions, vague leaves, and weight issues
5. runs `validate_rubric.py`, fixes blocking issues, and re-validates
6. saves a final `rubric.json` in the same directory as the paper

The generated rubric is meant to be faithful to the real PaperBench conventions, including:
- canonical `task_category` values only: `Code Development`, `Code Execution`, `Result Analysis`
- `sub_tasks` present on every node
- null or absent `task_category` on internal nodes
- non-null `task_category` and `finegrained_task_category` on leaves
- semantically meaningful child ordering, with `Code Development -> Code Execution -> Result Analysis` whenever those phases co-occur
- small local integer weights
- first-level decomposition by contribution or experimental block, not by paper sections unless sections are truly autonomous

## Expected input

Input is a directory containing at least one of:
- a paper PDF
- a sufficiently complete `paper.md`

Optional supporting files in the same directory:
- addendum or appendix extracts
- notes
- extra context files that clarify experiments or evaluation

## Generated outputs

The skill writes these artifacts into the input directory:
- `paper_analysis.md`
- `rubric.json`
- `coverage_review.md`
- `validation_report.txt`

These files act as checkpoints, so the skill can resume from partial progress instead of restarting from scratch.

## Multi-pass workflow

The skill implements the following passes:

### Pass 1 — Paper analysis
Reads the full paper and structures the experimental landscape: contributions, experiment families, datasets, baselines, metrics, pseudocode blocks, and major result tables.

### Pass 2 — Top-down rubric generation
Builds the rubric root first, then expands each major subtree incrementally. It uses the bundled structural principles and the most relevant annotated examples as guides.

### Pass 2.5 — Coverage review
Cross-checks the draft rubric against the paper and patches missing experiments, vague leaves, or weight mismatches.

### Pass 3 — Validation and repair
Runs `validate_rubric.py`, fixes all schema or structural errors, and resolves or justifies remaining warnings.

### Pass 4 — Finalization
Performs a last JSON sanity check and emits summary statistics for the saved rubric.

## Why the validator matters

`validate_rubric.py` is a core part of the workflow, not an optional helper.

It checks, among other things:
- schema conformance
- internal vs leaf `task_category` constraints
- required `sub_tasks`
- duplicate IDs
- ordering monotonicity
- weight plausibility
- structural statistics against benchmark ranges

This creates a generate-measure-correct loop rather than relying on self-critique alone.

## Installing the skill in Claude Code

Because this repository root contains `SKILL.md`, the repo itself is already a valid Claude Code skill folder.

A collaborator can typically use it in one of these ways:

1. Clone the repository and place it in their local Claude Code skills directory.
2. Clone it anywhere convenient and symlink or copy the folder into their local skills directory.
3. If they use a skill installer workflow, install it directly from the GitHub repository path.

If their setup expects the folder name to match the skill name, the local folder should be named `rubric-creator`.

## Using the skill

Invoke the skill on a paper directory.

Typical behavior:
- if `paper.md` is present, it is used as the primary paper source
- otherwise the skill extracts text from the PDF
- intermediate artifacts are written after each major pass
- if the skill is invoked again with `RESUME:`, it resumes from the earliest incomplete pass

## Reference provenance

The bundled references were produced from a dedicated PaperBench analysis pipeline and are meant to anchor generation in the actual benchmark rather than generic rubric-writing heuristics.

They include:
- benchmark-wide structural statistics
- code-derived schema constraints from the PaperBench codebase
- judge assumptions about ordering and node categories
- annotated case studies covering different rubric regimes

`SKILL.md` contains the operating procedure. The `reference/` directory contains the detailed knowledge that procedure relies on.

## Repository scope

This repository contains the `rubric-creator` skill only. It is not the full PaperBench project and it is not the pAI-Replicator repository.

## Current repository URL

GitHub repository:
[https://github.com/RiccardoN4/Rubric-creator-claude-skill](https://github.com/RiccardoN4/Rubric-creator-claude-skill)
