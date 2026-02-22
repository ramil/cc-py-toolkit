#!/usr/bin/env python3
"""
Wave Runner — Iterative battery test orchestrator for cc-py-toolkit v1.0.
Validates generated files, updates error registry, and produces wave reports.
"""

import json
import os
import sys
import datetime
from collections import defaultdict, Counter
from test_harness import COMPANIES
from validator import run_validation

REGISTRY_FILE = "error_registry.json"


def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {"version": "1.0.0", "waves": [], "errors": {}, "spec_patches": [], "score_history": []}


def save_registry(reg):
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(reg, f, indent=2)


def validate_run(run_id):
    """Validate a single run and return structured results"""
    c = COMPANIES[run_id - 1]
    code = c["code"]
    config_file = f"run{run_id:02d}_config_{code}.xlsx"
    migration_file = f"run{run_id:02d}_migration_{code}.xlsx"

    if not os.path.exists(config_file) or not os.path.exists(migration_file):
        return None

    results = run_validation(config_file, migration_file, c)
    summary = results.get("summary", {})

    # Extract failed check IDs
    fails = []
    for check in results.get("config_workbook", {}).get("checks", []):
        if not check.get("pass"):
            fails.append(f"{check['id']}:{check['name']}")
    for check in results.get("migration_file", {}).get("checks", []):
        if not check.get("pass"):
            fails.append(f"{check['id']}:{check['name']}")

    return {
        "run": run_id,
        "code": code,
        "name": c["name"],
        "industry": c["industry"],
        "benefits_approach": c.get("benefits_approach", "full"),
        "time_approach": c.get("time_approach", "full"),
        "score": summary.get("score_pct", 0),
        "passed": summary.get("total_pass", 0),
        "total": summary.get("total_checks", 0),
        "status": summary.get("validation_status", "ERROR"),
        "fails": fails
    }


def run_wave(wave_num, start_run, end_run):
    """Validate all runs in a wave and update registry"""
    reg = load_registry()

    wave_results = []
    for run_id in range(start_run, end_run + 1):
        result = validate_run(run_id)
        if result:
            wave_results.append(result)
            print(f"  Run {run_id:02d} ({result['code']}): {result['score']}% — {result['status']}")
        else:
            print(f"  Run {run_id:02d}: FILES NOT FOUND — skipping")

    if not wave_results:
        print("No results to process")
        return

    # Wave summary
    scores = [r["score"] for r in wave_results]
    avg = sum(scores) / len(scores) if scores else 0
    perfect = sum(1 for s in scores if s == 100)
    above95 = sum(1 for s in scores if s >= 95)
    above90 = sum(1 for s in scores if s >= 90)
    below90 = sum(1 for s in scores if s < 90)

    # Error frequency analysis
    fail_counter = Counter()
    for r in wave_results:
        for f in r["fails"]:
            fail_counter[f] += 1

    # Update error registry with new errors
    for err, count in fail_counter.items():
        if err not in reg["errors"]:
            reg["errors"][err] = {
                "first_seen_wave": wave_num,
                "occurrences": [],
                "total_count": 0,
                "fixed": False
            }
        reg["errors"][err]["occurrences"].append({"wave": wave_num, "count": count})
        reg["errors"][err]["total_count"] += count

    # Record wave
    wave_data = {
        "wave": wave_num,
        "runs": f"{start_run}-{end_run}",
        "timestamp": datetime.datetime.now().isoformat(),
        "count": len(wave_results),
        "avg_score": round(avg, 1),
        "perfect": perfect,
        "above_95": above95,
        "above_90": above90,
        "below_90": below90,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "top_failures": fail_counter.most_common(10),
        "results": wave_results
    }
    reg["waves"].append(wave_data)
    reg["score_history"].append({"wave": wave_num, "avg": round(avg, 1), "perfect": perfect, "count": len(wave_results)})

    save_registry(reg)

    # Print wave report
    print(f"\n{'='*60}")
    print(f"  WAVE {wave_num} SUMMARY (Runs {start_run}-{end_run})")
    print(f"{'='*60}")
    print(f"  Average Score:  {avg:.1f}%")
    print(f"  Perfect (100%): {perfect}/{len(wave_results)}")
    print(f"  >= 95%:         {above95}/{len(wave_results)}")
    print(f"  >= 90%:         {above90}/{len(wave_results)}")
    print(f"  < 90%:          {below90}/{len(wave_results)}")
    print(f"  Min: {min(scores):.1f}%  Max: {max(scores):.1f}%")
    print()

    if fail_counter:
        print("  TOP FAILURES THIS WAVE:")
        for err, count in fail_counter.most_common(10):
            # Check if this error is NEW (first seen this wave)
            marker = " ⭐NEW" if reg["errors"][err]["first_seen_wave"] == wave_num else ""
            print(f"    {count:2d}x  {err}{marker}")

    # Compare with previous wave
    if len(reg["score_history"]) >= 2:
        prev = reg["score_history"][-2]
        curr = reg["score_history"][-1]
        delta = curr["avg"] - prev["avg"]
        print(f"\n  WAVE-OVER-WAVE:")
        print(f"    Avg Score: {prev['avg']}% → {curr['avg']}% ({'+'if delta>=0 else ''}{delta:.1f}%)")
        print(f"    Perfect:   {prev['perfect']} → {curr['perfect']}")

    # Identify errors that persist across waves (need spec fix)
    persistent = []
    for err, data in reg["errors"].items():
        waves_seen = len(data["occurrences"])
        if waves_seen >= 2 and not data["fixed"]:
            persistent.append((err, data["total_count"], waves_seen))
    if persistent:
        print(f"\n  PERSISTENT ERRORS (seen in 2+ waves — NEED SPEC FIX):")
        for err, total, waves in sorted(persistent, key=lambda x: -x[1]):
            print(f"    {total:2d}x across {waves} waves: {err}")

    print(f"{'='*60}")

    return wave_data


def get_error_context_for_spec_update():
    """Generate a compact error summary for feeding back into spec updates"""
    reg = load_registry()

    # Get all unfixed errors sorted by frequency
    active_errors = {}
    for err, data in reg["errors"].items():
        if not data.get("fixed"):
            active_errors[err] = data["total_count"]

    sorted_errors = sorted(active_errors.items(), key=lambda x: -x[1])

    lines = ["ACTIVE ERRORS (unfixed, sorted by frequency):"]
    for err, count in sorted_errors[:20]:
        lines.append(f"  {count:3d}x  {err}")

    return "\n".join(lines)


def mark_errors_fixed(error_ids, patch_description):
    """Mark errors as fixed after a spec update"""
    reg = load_registry()
    for eid in error_ids:
        if eid in reg["errors"]:
            reg["errors"][eid]["fixed"] = True
    reg["spec_patches"].append({
        "timestamp": datetime.datetime.now().isoformat(),
        "description": patch_description,
        "errors_addressed": error_ids
    })
    save_registry(reg)
    print(f"Marked {len(error_ids)} errors as fixed: {patch_description}")


def final_report():
    """Generate a final summary across all waves"""
    reg = load_registry()

    print("\n" + "="*70)
    print("  FINAL ITERATIVE IMPROVEMENT REPORT")
    print("="*70)

    if not reg["score_history"]:
        print("  No waves recorded yet.")
        return

    print("\n  WAVE-BY-WAVE PROGRESSION:")
    for h in reg["score_history"]:
        bar = "█" * int(h["avg"] / 2) + "░" * (50 - int(h["avg"] / 2))
        print(f"    Wave {h['wave']}: {bar} {h['avg']}% (perfect: {h['perfect']}/{h['count']})")

    first = reg["score_history"][0]
    last = reg["score_history"][-1]
    improvement = last["avg"] - first["avg"]

    print(f"\n  OVERALL IMPROVEMENT: {first['avg']}% → {last['avg']}% ({'+' if improvement >= 0 else ''}{improvement:.1f}%)")
    print(f"  PERFECT SCORES:     {first['perfect']} → {last['perfect']}")

    # Error resolution stats
    total_errors = len(reg["errors"])
    fixed_errors = sum(1 for e in reg["errors"].values() if e.get("fixed"))
    print(f"\n  ERROR RESOLUTION: {fixed_errors}/{total_errors} unique errors fixed")

    # Spec patches
    if reg["spec_patches"]:
        print(f"\n  SPEC PATCHES APPLIED ({len(reg['spec_patches'])}):")
        for p in reg["spec_patches"]:
            ea = p['errors_addressed']
            count = ea if isinstance(ea, int) else len(ea)
            print(f"    - {p['description']} ({count} errors)")

    print("="*70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python wave_runner.py validate <wave_num> <start_run> <end_run>")
        print("  python wave_runner.py errors")
        print("  python wave_runner.py fix <error_ids_comma_sep> <description>")
        print("  python wave_runner.py report")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "validate":
        wave_num = int(sys.argv[2])
        start = int(sys.argv[3])
        end = int(sys.argv[4])
        run_wave(wave_num, start, end)
    elif cmd == "errors":
        print(get_error_context_for_spec_update())
    elif cmd == "fix":
        error_ids = sys.argv[2].split(",")
        desc = sys.argv[3]
        mark_errors_fixed(error_ids, desc)
    elif cmd == "report":
        final_report()
