"""Evaluate Release B with the shared production-provider runner and strict scorer."""

from pathlib import Path

from scripts.evaluate_release_a import main

CASES = Path(__file__).resolve().parents[1] / "tests/fixtures/release_b_prompts.json"

if __name__ == "__main__":
    raise SystemExit(main(default_cases=CASES, release_name="B"))
