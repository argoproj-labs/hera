lint:
	pflake8 src examples

format:
	black --verbose src tests examples conftest.py
	isort src tests examples conftest.py

typecheck:
	mypy --show-traceback --namespace-packages --explicit-package-bases -p hera

examples:
	python generate.py
	git diff --exit-code -- examples