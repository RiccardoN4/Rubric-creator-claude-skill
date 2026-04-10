#!/usr/bin/env python3
"""
validate_rubric.py — PaperBench Rubric Conformance Validator

Takes a generated rubric.json and produces a conformance report.
Checks schema validity, structural constraints, statistical conformance
against observed PaperBench benchmark ranges, and ordering patterns.

Usage:
    python validate_rubric.py <path_to_rubric.json> [--output <report_path>]

If --output is not specified, prints the report to stdout.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ============================================================================
# Constants: canonical values from paperbench/rubric/tasks.py
# ============================================================================

VALID_TASK_CATEGORIES = {"Code Development", "Code Execution", "Result Analysis", "Subtree"}
LEAF_TASK_CATEGORIES = {"Code Development", "Code Execution", "Result Analysis"}
VALID_FINEGRAINED = {
    "Environment & Infrastructure Setup",
    "Dataset and Model Acquisition",
    "Data Processing & Preparation",
    "Method Implementation",
    "Experimental Setup",
    "Evaluation, Metrics & Benchmarking",
    "Logging, Analysis & Presentation",
}

# ============================================================================
# Reference ranges from official-20 PaperBench analysis
# ============================================================================

REFERENCE = {
    "root_children": {"mean": 6.85, "median": 6.5, "iqr": (5, 8), "min": 2, "max": 13},
    "max_depth": {"mean": 5.80, "median": 5.0, "iqr": (5, 7), "min": 4, "max": 9},
    "avg_leaf_depth": {"mean": 4.47, "median": 4.16, "iqr": (3.69, 4.89), "min": 2.62, "max": 6.96},
    "avg_branching_factor": {"mean": 3.98, "median": 3.85, "iqr": (3.42, 4.35), "min": 2.65, "max": 6.08},
    "cd_share": {"mean": 0.531, "median": 0.528, "iqr": (0.375, 0.680), "min": 0.064, "max": 0.947},
    "ex_share": {"mean": 0.329, "median": 0.290, "iqr": (0.110, 0.453), "min": 0.030, "max": 0.925},
    "ra_share": {"mean": 0.140, "median": 0.124, "iqr": (0.033, 0.218), "min": 0.011, "max": 0.413},
    "leaf_req_words_cd": {"mean": 27.8, "median": 26, "iqr": (19, 35), "min": 3, "max": 106},
    "leaf_req_words_ex": {"mean": 42.9, "median": 41, "iqr": (28, 55), "min": 5, "max": 106},
    "leaf_req_words_ra": {"mean": 25.5, "median": 21, "iqr": (16, 33), "min": 6, "max": 85},
    "internal_req_words": {"mean": 22.2, "median": 21, "iqr": (14, 30), "min": 2, "max": 67},
}

# Phase ordering: CD=0, EX=1, RA=2
PHASE_ORDER = {"Code Development": 0, "Code Execution": 1, "Result Analysis": 2}


# ============================================================================
# Data structures
# ============================================================================

@dataclass
class Issue:
    severity: str  # "ERROR", "WARNING", "INFO"
    category: str
    message: str
    node_id: str = ""


@dataclass
class RubricStats:
    total_nodes: int = 0
    leaf_nodes: int = 0
    internal_nodes: int = 0
    max_depth: int = 0
    root_children: int = 0
    leaf_depths: list = field(default_factory=list)
    branching_factors: list = field(default_factory=list)
    leaf_types: Counter = field(default_factory=Counter)
    leaf_req_words: dict = field(default_factory=lambda: defaultdict(list))
    internal_req_words: list = field(default_factory=list)
    all_ids: list = field(default_factory=list)
    raw_weights: list = field(default_factory=list)
    depth1_weights: list = field(default_factory=list)
    ordering_monotonic: int = 0
    ordering_total: int = 0


# ============================================================================
# Tree traversal and statistics collection
# ============================================================================

def collect_stats(node: dict, depth: int, stats: RubricStats) -> None:
    """Recursively traverse the rubric tree and collect statistics.

    Defensive against malformed input: non-dict children and non-list
    sub_tasks are skipped rather than crashing, so the report is always
    produced even on structurally broken rubrics.
    """
    if not isinstance(node, dict):
        return

    stats.total_nodes += 1
    stats.all_ids.append(node.get("id", ""))

    weight = node.get("weight", 0)
    if isinstance(weight, (int, float)):
        stats.raw_weights.append(weight)

    sub_tasks = node.get("sub_tasks")
    # Defensive: treat non-list sub_tasks as empty (schema check will flag it)
    if not isinstance(sub_tasks, list):
        sub_tasks = []

    is_leaf = len(sub_tasks) == 0

    if is_leaf:
        stats.leaf_nodes += 1
        stats.leaf_depths.append(depth)
        cat = node.get("task_category")
        if cat:
            stats.leaf_types[cat] += 1
            words = len(node.get("requirements", "").split())
            stats.leaf_req_words[cat].append(words)
    else:
        stats.internal_nodes += 1
        stats.branching_factors.append(len(sub_tasks))
        words = len(node.get("requirements", "").split())
        stats.internal_req_words.append(words)

        if depth == 0:
            stats.root_children = len(sub_tasks)
            stats.depth1_weights = [
                c.get("weight", 0) for c in sub_tasks if isinstance(c, dict)
            ]

        # Check ordering monotonicity for this internal node
        check_ordering(node, stats)

        for child in sub_tasks:
            collect_stats(child, depth + 1, stats)

    if depth > stats.max_depth:
        stats.max_depth = depth


def get_leaf_types_in_subtree(node: dict) -> list:
    """Return ordered list of leaf task_categories in DFS order."""
    if not isinstance(node, dict):
        return []
    sub_tasks = node.get("sub_tasks")
    if not isinstance(sub_tasks, list):
        sub_tasks = []
    if len(sub_tasks) == 0:
        cat = node.get("task_category")
        return [cat] if cat else []
    result = []
    for child in sub_tasks:
        result.extend(get_leaf_types_in_subtree(child))
    return result


def check_ordering(node: dict, stats: RubricStats) -> None:
    """Check if leaf types within this internal node follow phase-monotonic ordering.

    Counts every internal node in the denominator (including single-phase
    subtrees, which are trivially monotonic). This matches the benchmark
    reference of 83.8% computed over all 2902 official internal nodes.
    """
    leaf_types = get_leaf_types_in_subtree(node)

    # Always count this internal node in the denominator
    stats.ordering_total += 1

    if len(leaf_types) < 2:
        # Single-leaf or empty subtree: trivially monotonic
        stats.ordering_monotonic += 1
        return

    # Collapse consecutive duplicates into phase blocks
    blocks = [leaf_types[0]]
    for t in leaf_types[1:]:
        if t != blocks[-1]:
            blocks.append(t)

    # Filter to known phases
    phases = [PHASE_ORDER.get(b, -1) for b in blocks if b in PHASE_ORDER]
    if len(phases) < 2:
        # Single phase type: trivially monotonic
        stats.ordering_monotonic += 1
        return

    is_monotonic = all(phases[i] <= phases[i + 1] for i in range(len(phases) - 1))
    if is_monotonic:
        stats.ordering_monotonic += 1


# ============================================================================
# Validation checks
# ============================================================================

def validate_schema(node: dict, depth: int, issues: list) -> None:
    """Recursively validate schema constraints from TaskNode.__post_init__."""
    if not isinstance(node, dict):
        issues.append(Issue(
            "ERROR",
            "schema",
            f"Node at depth {depth} is not a JSON object: {type(node)}",
        ))
        return

    node_id = node.get("id", f"<unnamed at depth {depth}>")

    # Required fields
    for req_field in ("id", "requirements", "weight", "sub_tasks"):
        if req_field not in node:
            issues.append(Issue("ERROR", "schema", f"Missing required field '{req_field}'", node_id))

    # Weight checks
    weight = node.get("weight")
    if weight is not None:
        if not isinstance(weight, (int, float)):
            issues.append(Issue("ERROR", "schema", f"Weight is not numeric: {type(weight)}", node_id))
        elif weight < 0:
            issues.append(Issue("ERROR", "schema", f"Weight is negative: {weight}", node_id))

    # sub_tasks type check
    sub_tasks = node.get("sub_tasks")
    if sub_tasks is not None and not isinstance(sub_tasks, list):
        issues.append(Issue("ERROR", "schema", f"sub_tasks is not a list: {type(sub_tasks)}", node_id))
        return

    sub_tasks = sub_tasks or []
    is_leaf = len(sub_tasks) == 0

    # task_category checks
    cat = node.get("task_category")
    if is_leaf:
        if not cat:
            issues.append(Issue("ERROR", "schema", "Leaf node missing task_category", node_id))
        elif cat not in LEAF_TASK_CATEGORIES:
            if cat == "Subtree":
                issues.append(Issue("ERROR", "schema",
                    "'Subtree' is a judge-internal value, not valid for dataset rubrics", node_id))
            else:
                issues.append(Issue("ERROR", "schema", f"Invalid task_category: '{cat}'", node_id))
    else:
        if cat is not None:
            issues.append(Issue("ERROR", "schema",
                f"Internal node has task_category='{cat}' (must be null/absent)", node_id))

    # finegrained_task_category checks
    fcat = node.get("finegrained_task_category")
    if fcat is not None and fcat not in VALID_FINEGRAINED:
        issues.append(Issue("ERROR", "schema", f"Invalid finegrained_task_category: '{fcat}'", node_id))

    if is_leaf and not fcat:
        issues.append(Issue("WARNING", "schema",
            "Leaf missing finegrained_task_category (all official leaves have one)", node_id))

    # Recurse
    for child in sub_tasks:
        if isinstance(child, dict):
            validate_schema(child, depth + 1, issues)
        else:
            issues.append(Issue("ERROR", "schema", f"sub_task is not a dict: {type(child)}", node_id))


def validate_root_conventions(node: dict, issues: list) -> None:
    """Check PaperBench root-level conventions that are actually stable in data/code."""
    if not isinstance(node, dict):
        issues.append(Issue(
            "ERROR",
            "root",
            f"Top-level JSON value is not an object: {type(node)}",
        ))
        return

    root_weight = node.get("weight")
    if root_weight != 1:
        issues.append(Issue("WARNING", "root",
            f"Root node weight is {root_weight}, expected 1. "
            "All official PaperBench rubrics use weight=1 for the root."))

    # Root should not have task_category (already caught by schema check,
    # but we make it explicit here for the root contract)
    sub_tasks = node.get("sub_tasks")
    if not isinstance(sub_tasks, list) or len(sub_tasks) == 0:
        issues.append(Issue("ERROR", "root",
            "Root node has no children. A valid rubric must have at least one subtask."))


def validate_statistics(stats: RubricStats, issues: list) -> None:
    """Compare collected statistics against reference ranges."""

    def check_range(value, ref_key, label, severity="WARNING"):
        ref = REFERENCE[ref_key]
        iqr_lo, iqr_hi = ref["iqr"]
        obs_min, obs_max = ref["min"], ref["max"]
        if value < obs_min or value > obs_max:
            issues.append(Issue("WARNING", "statistics",
                f"{label} = {value:.2f} is outside observed benchmark range "
                f"[{obs_min}, {obs_max}] (IQR: [{iqr_lo}, {iqr_hi}])"))
        elif value < iqr_lo or value > iqr_hi:
            issues.append(Issue("INFO", "statistics",
                f"{label} = {value:.2f} is outside IQR [{iqr_lo}, {iqr_hi}] "
                f"but within observed range [{obs_min}, {obs_max}]"))

    # Root children
    check_range(stats.root_children, "root_children", "Root children count")

    # Depth
    check_range(stats.max_depth, "max_depth", "Max depth")

    # Average leaf depth
    if stats.leaf_depths:
        avg_ld = sum(stats.leaf_depths) / len(stats.leaf_depths)
        check_range(avg_ld, "avg_leaf_depth", "Average leaf depth")

    # Branching factor
    if stats.branching_factors:
        avg_bf = sum(stats.branching_factors) / len(stats.branching_factors)
        check_range(avg_bf, "avg_branching_factor", "Average branching factor")

    # Leaf type shares
    total_leaves = stats.leaf_nodes
    if total_leaves > 0:
        cd_share = stats.leaf_types.get("Code Development", 0) / total_leaves
        ex_share = stats.leaf_types.get("Code Execution", 0) / total_leaves
        ra_share = stats.leaf_types.get("Result Analysis", 0) / total_leaves

        check_range(cd_share, "cd_share", "Code Development share")
        check_range(ex_share, "ex_share", "Code Execution share")
        check_range(ra_share, "ra_share", "Result Analysis share")

        if ra_share == 0:
            issues.append(Issue("WARNING", "statistics",
                "No Result Analysis leaves at all. Benchmark mean is 14.0%. "
                "Consider adding leaves that verify experimental claims."))

    # Requirement word lengths
    for cat, ref_key in [
        ("Code Development", "leaf_req_words_cd"),
        ("Code Execution", "leaf_req_words_ex"),
        ("Result Analysis", "leaf_req_words_ra"),
    ]:
        words_list = stats.leaf_req_words.get(cat, [])
        if words_list:
            avg_w = sum(words_list) / len(words_list)
            ref = REFERENCE[ref_key]
            iqr_lo, iqr_hi = ref["iqr"]
            if avg_w < ref["min"] or avg_w > ref["max"]:
                issues.append(Issue("WARNING", "statistics",
                    f"Average {cat} requirement length = {avg_w:.1f} words "
                    f"is outside observed range [{ref['min']}, {ref['max']}]"))

    # Internal requirement length
    if stats.internal_req_words:
        avg_iw = sum(stats.internal_req_words) / len(stats.internal_req_words)
        ref = REFERENCE["internal_req_words"]
        if avg_iw < ref["min"] or avg_iw > ref["max"]:
            issues.append(Issue("WARNING", "statistics",
                f"Average internal node requirement length = {avg_iw:.1f} words "
                f"is outside observed range [{ref['min']}, {ref['max']}]"))


def validate_ids(stats: RubricStats, issues: list) -> None:
    """Check for duplicate IDs."""
    id_counts = Counter(stats.all_ids)
    duplicates = {k: v for k, v in id_counts.items() if v > 1}
    if duplicates:
        for dup_id, count in duplicates.items():
            issues.append(Issue("WARNING", "ids",
                f"Duplicate id '{dup_id}' appears {count} times. "
                "IDs should be unique for unambiguous judge lookup."))


def validate_ordering(stats: RubricStats, issues: list) -> None:
    """Report on phase-ordering conformance."""
    if stats.ordering_total == 0:
        return
    mono_pct = (stats.ordering_monotonic / stats.ordering_total) * 100
    if mono_pct < 80:
        issues.append(Issue("WARNING", "ordering",
            f"Phase-monotonic ordering: {mono_pct:.1f}% of internal nodes "
            f"({stats.ordering_monotonic}/{stats.ordering_total}). "
            "Benchmark reference is 83.8%. Consider reordering children "
            "to follow Code Development -> Code Execution -> Result Analysis."))
    else:
        issues.append(Issue("INFO", "ordering",
            f"Phase-monotonic ordering: {mono_pct:.1f}% of internal nodes "
            f"({stats.ordering_monotonic}/{stats.ordering_total}). "
            "Benchmark reference is 83.8%."))


def validate_weights(stats: RubricStats, issues: list) -> None:
    """Check weight patterns."""
    # Depth-1 weight uniformity
    if stats.depth1_weights:
        unique_w = set(stats.depth1_weights)
        if len(unique_w) == 1:
            issues.append(Issue("INFO", "weights",
                "All root children have identical weights. "
                "Benchmark rubrics typically use non-uniform weights at depth 1 "
                "to distinguish main contributions from prerequisites."))

    # Check for non-integer weights
    non_int = [w for w in stats.raw_weights if isinstance(w, float) and w != int(w)]
    if non_int:
        issues.append(Issue("INFO", "weights",
            f"Found {len(non_int)} non-integer weights. "
            "Benchmark rubrics almost exclusively use integer weights."))


# ============================================================================
# Report generation
# ============================================================================

def generate_report(rubric_path: str, node: dict, stats: RubricStats, issues: list) -> str:
    """Generate a human-readable conformance report."""
    lines = []
    lines.append("=" * 72)
    lines.append("PAPERBENCH RUBRIC CONFORMANCE REPORT")
    lines.append("=" * 72)
    lines.append(f"File: {rubric_path}")
    lines.append("")

    # Summary statistics
    lines.append("--- STRUCTURAL METRICS ---")
    lines.append(f"Total nodes:          {stats.total_nodes}")
    lines.append(f"Leaf nodes:           {stats.leaf_nodes}")
    lines.append(f"Internal nodes:       {stats.internal_nodes}")
    lines.append(f"Max depth:            {stats.max_depth}")
    if stats.leaf_depths:
        avg_ld = sum(stats.leaf_depths) / len(stats.leaf_depths)
        lines.append(f"Avg leaf depth:       {avg_ld:.2f}")
    lines.append(f"Root children:        {stats.root_children}")
    if stats.branching_factors:
        avg_bf = sum(stats.branching_factors) / len(stats.branching_factors)
        lines.append(f"Avg branching factor: {avg_bf:.2f}")
    lines.append("")

    # Leaf type distribution
    lines.append("--- LEAF TYPE DISTRIBUTION ---")
    total_leaves = stats.leaf_nodes
    for cat in ["Code Development", "Code Execution", "Result Analysis"]:
        count = stats.leaf_types.get(cat, 0)
        pct = (count / total_leaves * 100) if total_leaves > 0 else 0
        ref_mean = REFERENCE[{"Code Development": "cd_share", "Code Execution": "ex_share",
                              "Result Analysis": "ra_share"}[cat]]["mean"] * 100
        lines.append(f"  {cat:20s}: {count:5d} ({pct:5.1f}%)  [benchmark mean: {ref_mean:.1f}%]")
    # Check for unknown categories
    for cat, count in stats.leaf_types.items():
        if cat not in LEAF_TASK_CATEGORIES:
            lines.append(f"  {cat:20s}: {count:5d} *** INVALID ***")
    lines.append("")

    # Ordering
    if stats.ordering_total > 0:
        mono_pct = (stats.ordering_monotonic / stats.ordering_total) * 100
        lines.append("--- PHASE ORDERING ---")
        lines.append(f"Monotonic internal nodes: {stats.ordering_monotonic}/{stats.ordering_total} ({mono_pct:.1f}%)")
        lines.append(f"Benchmark reference:      83.8%")
        lines.append("")

    # Issues
    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]
    infos = [i for i in issues if i.severity == "INFO"]

    lines.append(f"--- ISSUES: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info ---")
    lines.append("")

    if errors:
        lines.append("ERRORS (must fix):")
        for i, issue in enumerate(errors, 1):
            loc = f" [{issue.node_id}]" if issue.node_id else ""
            lines.append(f"  {i}. [{issue.category}]{loc} {issue.message}")
        lines.append("")

    if warnings:
        lines.append("WARNINGS (should fix):")
        for i, issue in enumerate(warnings, 1):
            loc = f" [{issue.node_id}]" if issue.node_id else ""
            lines.append(f"  {i}. [{issue.category}]{loc} {issue.message}")
        lines.append("")

    if infos:
        lines.append("INFO (for reference):")
        for i, issue in enumerate(infos, 1):
            loc = f" [{issue.node_id}]" if issue.node_id else ""
            lines.append(f"  {i}. [{issue.category}]{loc} {issue.message}")
        lines.append("")

    # Verdict
    lines.append("--- VERDICT ---")
    if len(errors) == 0 and len(warnings) == 0:
        lines.append("PASS: Rubric is schema-valid and statistically conformant.")
    elif len(errors) == 0:
        lines.append(f"PASS WITH WARNINGS: Schema-valid but {len(warnings)} statistical/structural warnings.")
    else:
        lines.append(f"FAIL: {len(errors)} schema errors must be fixed before the rubric can be used.")

    lines.append("=" * 72)
    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Validate a PaperBench rubric JSON against schema and statistical norms."
    )
    parser.add_argument("rubric", help="Path to rubric.json")
    parser.add_argument("--output", "-o", help="Path to save report (default: stdout)")
    args = parser.parse_args()

    # Load rubric
    rubric_path = Path(args.rubric)
    if not rubric_path.exists():
        print(f"Error: {rubric_path} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(rubric_path) as f:
            rubric = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {rubric_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Collect statistics (defensive: if the tree is structurally broken,
    # we still produce a report with whatever we managed to collect)
    stats = RubricStats()
    try:
        collect_stats(rubric, depth=0, stats=stats)
    except Exception as e:
        stats_error = True
        stats_error_msg = str(e)
    else:
        stats_error = False
        stats_error_msg = ""

    # Run validations
    issues = []

    if stats_error:
        issues.append(Issue("ERROR", "structure",
            f"Tree traversal crashed: {stats_error_msg}. "
            "The rubric JSON is structurally malformed. "
            "Statistics below may be incomplete."))

    validate_schema(rubric, depth=0, issues=issues)
    validate_root_conventions(rubric, issues)
    validate_statistics(stats, issues)
    validate_ids(stats, issues)
    validate_ordering(stats, issues)
    validate_weights(stats, issues)

    # Generate report
    report = generate_report(str(rubric_path), rubric, stats, issues)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"Report saved to {output_path}")
    else:
        print(report)

    # Exit code: 1 if errors, 0 otherwise
    errors = [i for i in issues if i.severity == "ERROR"]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
