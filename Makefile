# we mark all commands as `phony` to avoid any potential conflict with files in the CICD environment
.PHONY: lint format isort typecheck typecheck verify build

lint:
	pflake8 $(SRC_FOLDER)

format: isort
	black --verbose $(SRC_FOLDER) $(TEST_FOLDER) $(EXAMPLES_FOLDER) ${CONFTEST}

isort:
	isort $(SRC_FOLDER) $(TEST_FOLDER) $(EXAMPLES_FOLDER) ${CONFTEST}

typecheck:
	mypy --explicit-package-bases -p hera
	mypy tests

test:
	pytest -c tox.ini $(TEST_FOLDER)

verify: lint typecheck test
	echo "Lint, typecheck, test successfully completed!"

build:
	python -m build --sdist --wheel --outdir dist/ .
