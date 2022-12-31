OPENAPI_SPEC_URL = "https://raw.githubusercontent.com/argoproj/argo-workflows/master/api/openapi-spec/swagger.json"

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Lint the source and example directories
	@pflake8 src scripts docs examples

format: ## Format and sort imports for source, tests, etc.
	@black src scripts docs tests examples conftest.py
	@isort src scripts docs tests examples conftest.py

typecheck: ## Run typecheck on the project and report any issues
	@mypy -p hera --exclude src/hera/models

examples: ## Generate all the example Markdown files in `/docs` based on the examples directory
	@python scripts/examples.py
	@git diff --exit-code -- examples

service: ## Generate the Hera service based on Argo OpenAPI specifications
	@python scripts/service.py $(OPENAPI_SPEC_URL)
	@$(MAKE) format

models: ## Generate all the Argo Workflows models
	@datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/models/workflows \
		--base-class hera.ArgoBaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix
	@$(MAKE) format
