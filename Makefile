PY = python3
PIP = pip3


.PHONY: all
all:
	${PY} setup.py sdist


.PHONY: clean
clean:
	@rm -rf dist
	@rm -rf .mypy_cache
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf


.PHONY: dev
dev:
	${PIP} install -e .[dev]


.PHONY: install
install:
	${PIP} install .


.PHONY: style
style:
	@echo "Sorting Imports:"
	@isort ./src
	@echo "Done Sorting Imports"
	@echo "Styling"
	@black ./src
	@echo "Done Styling"
	@echo "Checking Code Format"
	@flake8 ./src && \
		([ $$? -eq 0 ] && echo "Styling Complete!! 🎉🎉") || \
		echo "❌^^^ Please address the above styling concerns ^^^❌"


.PHONY: type
type:
	@mypy


.PHONY: help
help:
	@echo "COMMANDS:"
	@echo "  all:     Build a distributible form of the package"
	@echo "  clean:   Remove builds, python caches, and mypy caches "
	@echo "  dev:     Create links to package for development changes"
	@echo "  install: Build and install package"
	@echo "  style:   Format the code base to meet pep8 standards"
	@echo "  type:    Typecheck the codebase"
	@echo "  help:    Show this message"
