ARGO_WORKFLOWS_VERSION="3.4.4"
OPENAPI_SPEC_URL="https://raw.githubusercontent.com/argoproj/argo-workflows/v$(ARGO_WORKFLOWS_VERSION)/api/openapi-spec/swagger.json"
SPEC_PATH="$(shell pwd)/argo-workflows-$(ARGO_WORKFLOWS_VERSION).json"

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
codegen: models services examples init-files

.PHONY: check-codegen
check-codegen: ## Check if the code is up to date
check-codegen:
	@$(MAKE) codegen
	git diff --exit-code || "Code is not up-to-date. Please run 'make codegen'"

.PHONY: format
format: ## Format and sort imports for source, tests, examples, etc.
	@poetry run ruff format .
	@poetry run ruff check . --fix

.PHONY: lint
lint:  ## Run a `lint` process on Hera and report problems
	@poetry run ruff check .
	@poetry run ruff format . --check
	@poetry run mypy -p hera

.PHONY: test
test:  ## Run tests for Hera
	@poetry run python -m pytest --cov-report=term-missing

.PHONY: workflows-models
workflows-models: ## Generate the Workflows models portion of Argo Workflows
	@touch $(SPEC_PATH)
	@poetry run python scripts/spec.py $(OPENAPI_SPEC_URL) $(SPEC_PATH)
	@poetry run datamodel-codegen \
		--input $(SPEC_PATH) \
		--snake-case-field \
		--target-python-version 3.8 \
		--output src/hera/workflows/models \
		--output-model-type pydantic.BaseModel \
		--base-class hera.shared._pydantic.BaseModel \
		--input-file-type jsonschema \
		--wrap-string-literal \
		--disable-appending-item-suffix \
		--disable-timestamp \
		--use-default-kwarg
	@find src/hera/workflows/models/ -name '*.py' -exec sed -i.bak 's/from pydantic import Field/from hera.shared._pydantic import Field/' {} +
	@find src/hera/workflows/models/ -name '*.bak' -delete
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) workflows
	@poetry run stubgen -o src -p hera.workflows.models && find src/hera/workflows/models -name '__init__.pyi' -delete
	@rm $(SPEC_PATH)
	@$(MAKE) format

.PHONY: events-models
events-models: ## Generate the Events models portion of Argo Workflows
	@touch $(SPEC_PATH)
	@poetry run python scripts/spec.py $(OPENAPI_SPEC_URL) $(SPEC_PATH)
	@poetry run datamodel-codegen \
		--input $(SPEC_PATH) \
		--snake-case-field \
		--target-python-version 3.8 \
		--output src/hera/events/models \
		--output-model-type pydantic.BaseModel \
		--base-class hera.shared._pydantic.BaseModel \
		--input-file-type jsonschema \
		--wrap-string-literal \
		--disable-appending-item-suffix \
		--disable-timestamp \
		--use-default-kwarg
	@find src/hera/events/models/ -name '*.py' -exec sed -i.bak 's/from pydantic import Field/from hera.shared._pydantic import Field/' {} +
	@find src/hera/events/models/ -name '*.bak' -delete
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) events
	@poetry run stubgen -o src -p hera.events.models && find src/hera/events/models -name '__init__.pyi' -delete
	@rm $(SPEC_PATH)
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
examples:  ## Generate documentation files for examples
	@(cd docs && poetry run python generate.py)

.PHONY: regenerate-test-data
regenerate-test-data:  ## Regenerates the test data from upstream examples and runs tests, report missing examples
regenerate-test-data: install-3.8
	find examples -name "*.yaml" -type f -delete
	HERA_REGENERATE=1 make test examples
	@poetry run python -m pytest -k test_for_missing_examples --runxfail
