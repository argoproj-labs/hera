SRC_FOLDER=src
TEST_FOLDER=tests
EXAMPLES_FOLDER=examples
CONFTEST=conftest.py

# we mark all commands as `phony` to avoid any potential conflict with files in the CICD environment
.PHONY: lint format isort typecheck typecheck verify build

lint:
	flake8 $(SRC_FOLDER)

format: isort
	black --verbose $(SRC_FOLDER) $(TEST_FOLDER) $(EXAMPLES_FOLDER) ${CONFTEST}

isort:
	isort $(SRC_FOLDER) $(TEST_FOLDER) $(EXAMPLES_FOLDER) ${CONFTEST}

typecheck:
	mypy --namespace-packages --explicit-package-bases -p hera
	mypy --namespace-packages tests

test:
	pytest --durations=5 $(TEST_FOLDER)

verify: lint typecheck test
	echo "Lint, typecheck, test successfully completed!"

build:
	python -m build --sdist --wheel --outdir dist/ .
