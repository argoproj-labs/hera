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

models:
	datamodel-codegen \
	  --url https://raw.githubusercontent.com/argoproj/argo-workflows/master/api/openapi-spec/swagger.json \
	  --use-annotated \
	  --snake-case-field \
	  --target-python-version 3.7 \
	  --output src/hera/models/workflows \
	  --base-class hera.ArgoBaseModel
	$(MAKE) format
