OPENAPI_SPEC_URL="https://raw.githubusercontent.com/argoproj/argo-workflows/v3.4.4/api/openapi-spec/swagger.json"

.PHONY: help
help: ## Showcase the help instructions for all the available `make` commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: ci
ci: ## Run all the CI checks
ci: CI=1
ci: lint test check-codegen

.PHONY: codegen
codegen: ## Generate all the code
codegen: models service examples

.PHONY: check-codegen
check-codegen: ## Check if the code is up to date
check-codegen: models service examples
	git diff --exit-code -- src/hera

.PHONY: format
format: ## Format and sort imports for source, tests, examples, etc.
	@poetry run black .
	@poetry run ruff . --fix

.PHONY: lint
lint:  ## Run a `lint` process on Hera and report problems
	@poetry run black . --check
	@poetry run ruff .
	@poetry run mypy -p hera

.PHONY: test
test:  ## Run tests for Hera
	@poetry run python -m pytest -v

.PHONY: workflows-models
workflows-models: ## Generate the Workflows models portion of Argo Workflows
	@poetry run datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/workflows/models \
		--base-class hera.workflows._base_model.BaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix \
		--disable-timestamp
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) workflows
	@$(MAKE) format

.PHONY: events-models
events-models: ## Generate the Events models portion of Argo Workflows
	@poetry run datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/events/models \
		--base-class hera.events._base_model.BaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix \
		--disable-timestamp
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) events
	@$(MAKE) format

.PHONY: models
models: ## Generate all the Argo Workflows models
models: workflows-models events-models

.PHONY: workflows-service
workflows-service:  ## Generate the Workflows service option of Hera
	@poetry run python scripts/service.py $(OPENAPI_SPEC_URL) workflows
	$(MAKE) format

.PHONY: events-service
events-service:  ## Generate the events service option of Hera
	@poetry run python scripts/service.py $(OPENAPI_SPEC_URL) events
	$(MAKE) format

.PHONY: service
services:  ## Generate the services of Hera
services: workflows-service events-service

.PHONY: examples
examples:  ## Generate all the examples
	@(cd docs && poetry run python generate.py)

.PHONY: regenerate-test-data
regenerate-test-data:  ## Regenerates the test data from upstream examples and runs tests
	HERA_REGENERATE=1 make test examples
