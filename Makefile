SRC_FOLDER=src
TEST_FOLDER=tests
EXAMPLES_FOLDER=examples

lint:
	flake8 $(SRC_FOLDER)

format:
	black --verbose $(SRC_FOLDER) $(TEST_FOLDER) $(EXAMPLES_FOLDER)

typecheck:
	mypy --namespace-packages --explicit-package-bases -p hera
	mypy --namespace-packages tests

test:
	pytest --durations=5 $(TEST_FOLDER)

verify: lint typecheck test
	echo "Lint, typecheck, test successfully completed!"


