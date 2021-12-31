PY = python3
PIP = pip3

ifndef COV_FILE
export COV_FILE="${PWD}/tests/test_configs/cov/coverage.cfg"
endif


.PHONY: all
all:
	${PY} setup.py sdist


.PHONY: clean
clean: clean-cov
	@rm -rf dist .mypy_cache .pytest_cache htmlcov
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf


.PHONY: clean-cov
clean-cov:
	@rm -f .coverage*


.PHONY: dev
dev:
	${PIP} install -e .[dev]


.PHONY: install
install:
	${PIP} install .


.PHONY: style
style:
	@echo "================================= SRC ================================"
	@echo "Sorting Imports:"
	@${PY} -m isort ./src
	@echo "Done Sorting Imports"
	@echo "Styling"
	@${PY} -m black ./src
	@echo "Done Styling"
	@echo "Checking Code Format"
	@${PY} -m flake8 ./src && \
		([ $$? -eq 0 ] && echo "Styling Complete!! 🎉🎉") || \
		echo "❌^^^ Please address the above styling concerns ^^^❌"
	@echo "====================================================================="


.PHONY: style-extras
style-extras:
	@echo "=============================== EXTRA ==============================="
	@echo "Sorting Imports:"
	@${PY} -m isort ./tests ./mocks
	@echo "Done Sorting Imports"
	@echo "Styling"
	@${PY} -m black ./tests ./mocks
	@echo "Done Styling"
	@echo "Checking Code Format"
	@${PY} -m flake8 ./tests && \
		([ $$? -eq 0 ] && echo "Extra Styling Complete!! 🎉🎉") || \
		echo "🔎^^^ Here are some styling suggestions ^^^🔎"
	@echo "====================================================================="


.PHONY: style-all
style-all: style style-extras


.PHONY: test
test:
	@${PY} -m pytest -v


.PHONY: test-cov
test-cov:
	@${PY} -m pytest -v --cov-config=${COV_FILE} --cov=./src
	@rm -f .coverage*


.PHONY: test-cov-html
test-cov-html:
	@${PY} -m pytest -v --cov-config=${COV_FILE} --cov=./src --cov-report html
	@rm -f .coverage*


.PHONY: type
type:
	@${PY} -m mypy


.PHONY: help
help:
	@echo "COMMANDS:"
	@echo "  all: ------------ Build a distributible form of the package"
	@echo "  clean: ---------- Remove builds, python caches, and mypy caches, pytest caches"
	@echo "  clean-cov: ------ Remove coverage binaries"
	@echo "  dev: ------------ Create links to package for development changes"
	@echo "  install: -------- Build and install package"
	@echo "  style: ---------- Format the code base to meet pep8 standards"
	@echo "  style-tests: ---- Format the test suite and mocks to meet pep8 standards"
	@echo "  style-all: ------ Run the two previous commands"
	@echo "  test: ----------- Run tests"
	@echo "  test-cov: ------- Run tests with coverage report"
	@echo "  test-cov-html: -- Run tests with coverage report as html"
	@echo "  type: ----------- Typecheck the codebase"
	@echo "  help: ----------- Show this message"
