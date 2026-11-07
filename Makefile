.PHONY: check check-fast check-slow

# Four workers, because more add memory and almost no speed. CI sets its own number.
PYTEST_WORKERS ?= 4
# Exit code 5 only means no tests ran: a project may have no slow tests, for example.
PYTEST = python3 -m pytest -q -n $(PYTEST_WORKERS) $(PYTEST_MARK) $(PYTEST_ARGS) || test $$? -eq 5

# Foundations: add a test command under the check target, one per line, once there is a real test to run.
# Use $(PYTEST), so it gets the workers and the markers: cd your-foundation && $(PYTEST)
check:
	python3 scripts/check.py
	@python3 -c "import xdist, pandas" 2>/dev/null || { echo "Python packages are missing or out of date. Run: python -m pip install -r requirements.txt"; exit 1; }
	python3 data/quality/run_checks.py
	cd normalized-data-model && $(PYTEST)
	cd mcp && $(PYTEST)
	cd measures && $(PYTEST)
	cd gap_finder && $(PYTEST)
	cd uncf && $(PYTEST)

# For while you work: the same commands, without the tests marked slow. Run make check before pushing.
check-fast:
	$(MAKE) check PYTEST_MARK='-m "not slow"'

# Only the slow tests. CI runs this and check-fast on separate machines.
check-slow:
	$(MAKE) check PYTEST_MARK='-m slow'
