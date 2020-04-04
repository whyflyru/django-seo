.PHONY: clean clean-test clean-pyc clean-build docs help lint
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-cache ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -rf reports/
	rm -fr .pytest_cache

clean-cache: ## remove pip cache
	rm -rf .cache

clean-venv: ## remove local venv
	rm -rf `pipenv --venv`

PR = pipenv run
PRP = pipenv run py.test
PRPM = pipenv run python manage.py
PTARGS = --nomigrations --showlocals --fail-on-template-vars
COVARGS = --cov-config .coveragerc --cov-report html --cov djangoseo
TCARGS = --timeout=10 -n auto

lint: clean-test ## check style with flake8
	$(PR) flake8 setup.py docs djangoseo tests

env-prepare: ## install environment
	pipenv install --dev
	pipenv clean

test: clean-test ## run tests quickly with the default Python
	$(PRP) $(PTARGS) $(TEST)

test-travis: ## run tests on every Python version with tox
	pipenv run python setup.py test

test-all-parallel: ## run tests on every Python version with tox in parallel
	pipenv run tox -p auto

coverage: clean-test ## check code coverage quickly with the default Python
	$(PRP) $(COVARGS) --cov-append
	$(BROWSER) reports/unit/index.html

bump-version-patch: ## update patch version (update, commit, tag)
	bumpversion patch --verbose

bump-version-minor: ## update minor version (update, commit, tag)
	bumpversion minor --verbose

bump-version-major: ## update major version (update, commit, tag)
	bumpversion major --verbose

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	pipenv run python setup.py install
