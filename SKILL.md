---
name: rubric-creator
description: Generate a PaperBench-compatible rubric.json from an ML paper folder containing a PDF and optional paper.md/addendum, using checkpointed multi-pass analysis, top-down rubric construction, and validator-driven repair.
user_invocable: true
---

# rubric-creator

You are **rubric-creator**. Given a folder containing at least an ML paper PDF, generate a `rubric.json` in the exact PaperBench format and save it in that same folder.

This skill is procedural. The quantitative rules, schema details, and worked examples live in bundled references and must be read at the points specified below. Do not restate those references from memory when the skill can read them directly.

## 1. Resolve paths and inputs

Treat the user-provided path as `INPUT_DIR`.

If the user gives a file path instead of a directory:
- If it is a `paper.md` or `*.pdf`, set `INPUT_DIR` to its parent directory.
- Otherwise stop and explain that the skill expects a paper directory.

Set:

```text
SKILL_DIR = directory containing this SKILL.md
INPUT_DIR = target paper directory
OUTPUT_RUBRIC = {INPUT_DIR}/rubric.json
```

Expected input contents:
- Required: at least one paper PDF, unless a complete `paper.md` is already present.
- Optional: `paper.md`, addendum, notes, appendix extracts, or other supporting files.

Primary output:
- `{INPUT_DIR}/rubric.json`

Checkpoint artifacts:
- `{INPUT_DIR}/paper_analysis.md`
- `{INPUT_DIR}/coverage_review.md`
- `{INPUT_DIR}/validation_report.txt`

## 2. Mandatory reference-loading protocol

Read these files before generating or editing the rubric:

1. `reference/structural_principles_complete.md`
2. `reference/rubric_schema_reference.md`
3. `reference/rubric_schema.json`
4. `validate_rubric.py`

Read annotated examples selectively, not all by default. Choose the 1-2 closest examples after Pass 1:
- `stochastic-interpolants_annotated.md` for small, Code Development-heavy papers with compact structure.
- `robust-clip_annotated.md` for result-heavy papers with strong `Result Analysis` presence.
- `all-in-one_annotated.md` for a typical mixed case near benchmark averages.
- `sample-specific-masks_annotated.md` for execution-heavy papers with repeated benchmark templates.
- `lbcs_annotated.md` for very large, deep, repeated benchmark matrices.

Use the references as follows:
- `structural_principles_complete.md` is the source of structural priors, quantitative ranges, ordering patterns, weight behavior, and rubric-size calibration.
- `rubric_schema_reference.md` is the source of exact code-level constraints and canonical enums.
- `rubric_schema.json` is the formal machine-readable schema.
- `validate_rubric.py` is the final repair loop and conformance backstop.
- The annotated examples are pattern libraries for decomposition choices and leaf phrasing.

Do not invent schema fields, enum variants, or validation rules that are not present in these references.

## 3. Global operating rules

Follow these rules in every pass:

1. The only valid generated `task_category` strings are exactly:
   - `Code Development`
   - `Code Execution`
   - `Result Analysis`
2. Never generate `Subtree`. It exists in the codebase for internal judge logic, not for authored rubric JSON.
3. Internal nodes must not carry a non-null `task_category`.
4. Leaf nodes must carry a non-null `task_category`.
5. Generate `finegrained_task_category` for every leaf, using only the exact valid strings documented in `reference/rubric_schema_reference.md` and `reference/rubric_schema.json`.
6. Every node must contain `sub_tasks`. Leaves must use `"sub_tasks": []`.
7. Child order is semantically meaningful. Within every subtree, order leaf phases as `Code Development` -> `Code Execution` -> `Result Analysis` whenever those phases appear.
8. Distinguish `Code Execution` from `Result Analysis` lexically:
   - compute/run/execute/produce/report a measured artifact -> `Code Execution`
   - conclude/show/is around/is better than/interprets a result -> `Result Analysis`
9. Size the rubric from experimental complexity, not paper length. Use the calibration guidance in `reference/structural_principles_complete.md`.
10. First-level decomposition should follow contributions or experimental blocks, not paper sections, except where the paper contains truly autonomous experimental sections.
11. Shared infrastructure blocks such as datasets, metrics, common backbones, or reusable setup can be promoted to the first level with low weight when they support multiple downstream branches.
12. Reuse named procedures, algorithms, or pseudocode blocks from the paper as intermediate nodes when that matches the paper's internal organization.
13. Use small local integer weights. Do not invent elaborate scales.
14. Node IDs must be unique. Prefer stable descriptive slugs over UUIDs.
15. Preserve completed work on resume. Never regenerate the whole rubric if only one subtree or validation issue needs repair.

## 4. RESUME protocol

If the invocation starts with `RESUME:`, do not restart from scratch.

Instead, inspect the artifacts already present in `INPUT_DIR` and resume from the earliest incomplete pass:

1. If `paper_analysis.md` is missing or clearly incomplete, resume at Pass 1.
2. Else if `rubric.json` is missing, resume at Pass 2.
3. Else if `rubric.json` exists but contains incomplete structure, resume at Pass 2 and expand only the incomplete branches.
4. Else if `coverage_review.md` is missing, resume at Pass 2.5.
5. Else if `validation_report.txt` is missing, or if the rubric still has unresolved schema/validation problems, resume at Pass 3.
6. Else run Pass 4 and emit the completion banner.

When resuming:
- Read all existing artifacts first.
- Preserve good content already on disk.
- Improve only missing or weak sections.
- Overwrite artifacts in place only after integrating with the existing content.

Treat a rubric as structurally incomplete when one or more nodes have empty `sub_tasks` but the surrounding evidence suggests that they should expand further. Typical signs:
- the node bundles multiple datasets, experiments, or claims in one requirement
- the parent subtree is missing expected `Code Development` / `Code Execution` / `Result Analysis` phase coverage
- the node names a method family, benchmark suite, ablation block, or named procedure that the paper clearly decomposes further

## 5. Pass 1 - Paper analysis

Goal: build a structured understanding of the paper before drafting any rubric tree.

Procedure:

1. Prefer `{INPUT_DIR}/paper.md` if it exists and is readable.
2. Otherwise convert the paper PDF into readable text.
   - First try available local tools such as `pdftotext`.
   - If needed, use Python with `pymupdf` or another suitable library.
   - If a dependency is missing, install it if the environment permits.
3. Read the full paper, not only the abstract and experiments.
4. Also read any addendum or notes in `INPUT_DIR` when they clarify experimental setup, metrics, or appendix-only results.
5. Extract and organize at minimum:
   - title and one-sentence paper thesis
   - main contributions
   - experiment families
   - datasets or environments per family
   - baselines, variants, and ablations
   - metrics and evaluation protocols
   - named procedures, algorithms, or pseudocode blocks
   - major tables and figures tied to reproducible claims
   - dependencies between experiments
6. Estimate rubric scale using the calibration rule from `reference/structural_principles_complete.md`:

```text
rubric_size ≈ experiment_families × datasets_per_family × baselines_per_dataset × phases_per_bundle
```

7. Write `{INPUT_DIR}/paper_analysis.md` with structured sections that make Passes 2-3 easy:
   - Paper summary
   - Contributions
   - Experimental map
   - Dependencies
   - Named procedures / reusable modules
   - Key tables and figures
   - Complexity estimate and likely rubric size band
   - Likely first-level decomposition candidates

Checkpoint requirement:
- Save `paper_analysis.md` to disk before doing any rubric generation.

Resume rule:
- If `RESUME:` is active and `paper_analysis.md` already exists and is usable, skip directly to Pass 2.

## 6. Pass 2 - Top-down rubric generation

Goal: construct the rubric tree incrementally from the root downward.

Before generating:

1. Re-read `reference/structural_principles_complete.md`.
2. Re-read `reference/rubric_schema_reference.md`.
3. Use the complexity estimate from Pass 1 to select the 1-2 most relevant annotated examples in `reference/annotated_examples/`.
4. Read those examples fully before choosing the first-level structure.

Generation procedure:

1. Start with the root and its direct children only.
   - The root must have `weight: 1`.
   - The root should summarize the overall reproduction target at a high level.
2. Decompose the first level by contributions or experimental blocks, not by table of contents sections, unless the paper truly organizes independent evaluation programs by section.
   - For each root child you create, identify its intended paper anchor before expanding it further.
   - Valid anchors include a numbered figure, numbered table, named section or subsection, named algorithm, equation block, procedure, or a clearly stated contribution in the abstract/introduction.
3. Assign root-child weights locally relative to siblings. Use the first-level weighting priors from `reference/structural_principles_complete.md`.
4. Then expand one root child at a time.
5. For each subtree, expand one level at a time until the leaf requirements become specific, binary, and judgeable.
6. Save `rubric.json` after each major subtree expansion. Do not wait until the whole tree is finished.

Per-node requirements:

1. Every node must include:
   - `id`
   - `requirements`
   - `weight`
   - `sub_tasks`
2. The root must have at least one child.
3. Internal nodes:
   - omit `task_category`, or set it to `null`
   - may omit `finegrained_task_category`, or set it to `null`
4. Leaf nodes:
   - must set `task_category`
   - must set `finegrained_task_category`
   - must set `"sub_tasks": []`
5. Use only the canonical task-category strings.
6. Use only the valid fine-grained strings from the schema references.
7. Use unique descriptive IDs, ideally slug-like and semantically traceable.
8. Use small local integer weights, typically 1-3 unless a strong reason from the paper structure justifies more.

Structural guidance:

1. Reuse named algorithms, procedures, benchmark suites, or ablation programs as intermediate nodes when that improves alignment with the paper.
2. Promote shared setup blocks to the first level when they feed multiple downstream result branches.
3. For benchmark-heavy papers, scale with repeated low-branching templates rather than flat giant sibling lists.
4. If a branch naturally contains all three phases, arrange them as:
   - implement / prepare -> `Code Development`
   - run / compute / produce metrics -> `Code Execution`
   - compare / interpret / verify numerical claims -> `Result Analysis`

Leaf-writing guidance:

1. Leaves must be concrete enough for binary judging.
2. Avoid vague requirements like "The method is implemented correctly."
3. Prefer verifiable claims tied to artifacts, procedures, outputs, or reported outcomes.
4. Match requirement length and phrasing style to the benchmark patterns described in `reference/structural_principles_complete.md` and illustrated in the annotated examples.

Checkpoint requirement:
- Save `{INPUT_DIR}/rubric.json` after:
  - first-level creation
  - every major root-child subtree expansion
  - the first fully completed draft

Resume rule:
- If `RESUME:` is active and `rubric.json` exists, inspect it for incomplete branches and continue only from those branches.

## 7. Pass 2.5 - Coverage review

Goal: compare the draft rubric against the paper and close omissions before formal validation.

Procedure:

1. Read `paper_analysis.md` and `rubric.json` together.
2. Produce `{INPUT_DIR}/coverage_review.md` answering:
   - Which contributions and experimental programs are covered?
   - Which contributions or experiments are missing?
   - Go through the key figures, tables, algorithms, and named experimental blocks listed in `paper_analysis.md` and verify that each one has at least one corresponding rubric branch.
   - Which leaves are too vague for binary grading?
   - Do first-level weights reflect the paper's relative emphasis?
   - Is the leaf-type mix reasonable for this paper family?
2b. For every first-level child of the root, and only for first-level children, verify that it has a direct anchor in the paper:
   - a numbered figure
   - a numbered table
   - a named section or subsection
   - a named algorithm, equation block, or procedure
   - or a clearly stated contribution in the abstract/introduction

   If a first-level node does not have a direct anchor, mark it as suspicious in `coverage_review.md`.
   Suspicious first-level nodes must then be either:
   - removed, if they do not correspond to a real paper element
   - or reconciled/merged into an anchored node that does correspond to a real paper element
3. For every missing contribution or experiment, add the missing nodes.
4. For every suspicious first-level node, remove it or reconcile it with a real anchored paper element.
5. For every vague leaf, either rewrite it into a crisp binary requirement or split it into several smaller leaves.
6. Re-check ordering, IDs, and weight reasonableness after the edits.
7. Save both `coverage_review.md` and the updated `rubric.json`.

Checkpoint requirement:
- `coverage_review.md` must exist before moving to validation.

## 8. Pass 3 - Programmatic validation and repair

Goal: use the bundled validator as a repair loop, not as a single-shot check.

Run exactly:

```bash
python {SKILL_DIR}/validate_rubric.py {INPUT_DIR}/rubric.json --output {INPUT_DIR}/validation_report.txt
```

Validation loop:

1. Run the validator.
2. Read `{INPUT_DIR}/validation_report.txt` completely.
3. For every `ERROR`:
   - treat it as blocking
   - fix the rubric
   - re-run validation
4. For every `WARNING`:
   - decide whether it is a genuine conformance problem or a paper-specific exception
   - if it is a real problem, fix it and re-run validation
   - if it is justified by the paper, keep the rubric and record the justification
5. Repeat until:
   - there are zero errors, and
   - all warnings are either corrected or explicitly justified
6. Cap the loop at 5 iterations.
7. After the final validation run, append a short `Warning Justifications` section to `validation_report.txt` for any retained warnings.
8. Save the final `rubric.json` and `validation_report.txt`.

Repair priorities:

1. Schema and structural violations first.
2. Missing or invalid leaf categories next.
3. Ordering violations next.
4. Weight pathologies next.
5. Statistical warnings last, only when they are not paper-specific.

Never keep a schema error. A rubric with schema errors is not complete.

## 9. Pass 4 - Finalization

Before finishing:

1. Verify that `rubric.json` is valid JSON and readable.
2. Re-open the saved file once to ensure the serialized result is not truncated or malformed.
3. Compute and report:
   - total nodes
   - total leaves
   - leaf-type distribution
   - maximum depth
   - saved output path

Then print a completion banner in this style:

```text
============================================================
Rubric generation complete
Nodes: <total_nodes> | Leaves: <leaf_nodes> | Max depth: <max_depth>
Leaf types: Code Development=<n>, Code Execution=<n>, Result Analysis=<n>
Saved: <INPUT_DIR>/rubric.json
============================================================
```

## 10. Failure handling and quality bar

If you encounter missing inputs, unreadable PDFs, or extraction failures:
- try a second extraction method before giving up
- preserve any partial artifacts already created
- record what was attempted in the relevant checkpoint file

If the paper is unusually theoretical or structurally atypical:
- still obey schema constraints
- justify any retained validation warnings in `validation_report.txt`
- keep the rubric aligned to the paper's experimental reality rather than forcing benchmark-average proportions mechanically

The skill succeeds only when:
- `paper_analysis.md` exists
- `rubric.json` exists and is valid
- `coverage_review.md` exists
- `validation_report.txt` exists
- the rubric uses canonical PaperBench categories and ordering
- all validator errors are resolved
