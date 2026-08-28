#!/usr/bin/env python3
"""Run the complete, read-only pre-publication quality gate.

The default mode copies the current working tree to a temporary directory, runs
the canonical synchronizers there, verifies that they would not change the
publication, and then executes every repository QA suite. The source working
tree is never modified.

Use --fix deliberately to synchronize the source tree in place before running
the same QA suites. Content is not generated or rewritten by this wrapper; it
only invokes the deterministic synchronizers already controlled by README.md.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPTS = (
    "apply_seo.py",
    "feature_sync.py",
    "engagement_sync.py",
    "phase5_sync.py",
    "phase6_sync.py",
    "epic_passport_sync.py",
    "telemetry_sync.py",
)
QA_SCRIPTS = (
    "site_qa.py",
    "seo_qa.py",
    "feature_qa.py",
    "engagement_qa.py",
    "phase5_qa.py",
    "phase6_qa.py",
    "telemetry_qa.py",
    "season_filter_qa.py",
    "method_guide_qa.py",
    "season_pages_qa.py",
    "structured_metadata_qa.py",
    "statistics_qa.py",
    "advanced_archive_qa.py",
)
IGNORED_NAMES = {".git", "__pycache__", ".pytest_cache", ".DS_Store"}


def run_script(root: Path, script: str) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / script)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def copy_working_tree(destination: Path) -> None:
    shutil.copytree(
        ROOT,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*IGNORED_NAMES),
    )


def relative_files(root: Path) -> set[Path]:
    files: set[Path] = set()
    for path in root.rglob("*"):
        if any(part in IGNORED_NAMES for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.add(path.relative_to(root))
    return files


def changed_files(source: Path, synchronized: Path) -> list[str]:
    source_files = relative_files(source)
    synchronized_files = relative_files(synchronized)
    changes: list[str] = []
    for relative in sorted(source_files | synchronized_files):
        original = source / relative
        generated = synchronized / relative
        if relative not in source_files:
            changes.append(f"generated: {relative}")
        elif relative not in synchronized_files:
            changes.append(f"removed: {relative}")
        elif not filecmp.cmp(original, generated, shallow=False):
            changes.append(f"out of sync: {relative}")
    return changes


def synchronize(root: Path) -> list[tuple[str, int, str]]:
    results: list[tuple[str, int, str]] = []
    for script in SYNC_SCRIPTS:
        code, output = run_script(root, script)
        results.append((script, code, output))
        if code:
            break
    return results


def run_qa(root: Path) -> list[tuple[str, int, str]]:
    return [(script, *run_script(root, script)) for script in QA_SCRIPTS]


def report_results(title: str, results: list[tuple[str, int, str]]) -> bool:
    print(f"\n{title}")
    passed = True
    for script, code, output in results:
        status = "PASS" if code == 0 else "FAIL"
        print(f"- {script}: {status}")
        if output and (code or "WARNING:" in output):
            for line in output.splitlines():
                print(f"  {line}")
        passed = passed and code == 0
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a publication before deployment")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="run canonical synchronizers in the source tree before validating",
    )
    args = parser.parse_args()

    print("LCA of the Impossible — Pre-publication QA")
    print(f"Source: {ROOT}")

    drift: list[str] = []
    if args.fix:
        validation_root = ROOT
        sync_results = synchronize(validation_root)
        sync_passed = report_results("Deterministic synchronization", sync_results)
        qa_results = run_qa(validation_root) if sync_passed else []
    else:
        qa_results = run_qa(ROOT)
        temporary = tempfile.TemporaryDirectory(prefix="lca-publication-qa-")
        validation_root = Path(temporary.name) / "repository"
        copy_working_tree(validation_root)
        sync_results = synchronize(validation_root)
        if all(code == 0 for _, code, _ in sync_results):
            drift = changed_files(ROOT, validation_root)
        sync_passed = report_results("Deterministic synchronization", sync_results)
    if drift:
        sync_passed = False
        print("\nPublication files are not synchronized:")
        for change in drift:
            print(f"- {change}")
        print("Run `python scripts/publication_qa.py --fix`, review the diff, and commit it.")

    qa_passed = report_results("Validation suites", qa_results) if qa_results else False

    if sync_passed and qa_passed:
        print("\nPRE-PUBLICATION QA: PASS")
        return 0
    print("\nPRE-PUBLICATION QA: FAIL", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
