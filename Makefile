OPENAPI_SPEC_URL="https://raw.githubusercontent.com/argoproj/argo-workflows/v3.4.4/api/openapi-spec/swagger.json"

.PHONY: help
help: ## Showcase the help instructions for all the available `make` commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Run poetry install with default behaviour
	@poetry env use system
	@poetry install

.PHONY: install-3.8
install-3.8: ## Install python3.8 for generating test data
	@poetry env use 3.8
	@poetry install

.PHONY: ci
ci: ## Run all the CI checks
ci: CI=1
ci: lint test check-codegen

.PHONY: codegen
codegen: ## Generate all the code (models, services, examples, and init files)
codegen: models services examples init-files format

.PHONY: check-codegen
check-codegen: ## Check if the code is up to date
check-codegen: codegen format
	git diff --exit-code || "Code is not up-to-date. Please run 'make codegen'"

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
	@poetry run python -m pytest --cov-report=term-missing

.PHONY: workflows-models
workflows-models: ## Generate the Workflows models portion of Argo Workflows
	@poetry run datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/workflows/models \
		--base-class hera.shared._base_model.BaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix \
		--disable-timestamp \
		--use-default-kwarg
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) workflows
	@poetry run stubgen -o src -p hera.workflows.models && find src/hera/workflows/models -name '__init__.pyi' -delete
	@$(MAKE) format

.PHONY: events-models
events-models: ## Generate the Events models portion of Argo Workflows
	@poetry run datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/events/models \
		--base-class hera.shared._base_model.BaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix \
		--disable-timestamp \
		--use-default-kwarg
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) events
	@poetry run stubgen -o src -p hera.events.models && find src/hera/events/models -name '__init__.pyi' -delete
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

.PHONY: services
services:  ## Generate the services of Hera
services: workflows-service events-service

.PHONY: init-files
init-files:  ## Generate the init-files of Hera
init-files:
	@poetry run python scripts/init_files.py
	$(MAKE) format

.PHONY: examples
examples:  ## Generate all the examples
	@(cd docs && poetry run python generate.py)

.PHONY: regenerate-test-data
regenerate-test-data:  ## Regenerates the test data from upstream examples and runs tests, report missing examples
regenerate-test-data: install-3.8
	find examples -name "*.yaml" -type f -delete
	HERA_REGENERATE=1 make test examples
	@poetry run python -m pytest -k test_for_missing_examples --runxfail
