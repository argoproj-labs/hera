OPENAPI_SPEC_URL="https://raw.githubusercontent.com/argoproj/argo-workflows/v3.4.4/api/openapi-spec/swagger.json"

.PHONY: help
help: ## Showcase the help instructions for all the available `make` commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: format
format: ## Format and sort imports for source, tests, examples, etc.
	@black src docs tests scripts examples conftest.py
	@isort src docs tests scripts examples conftest.py

.PHONE: lint
lint:  ## Run a `lint` process on Hera and report problems
	tox -e lint

.PHONE: typecheck
typecheck:  ## Run a `typecheck` process on Hera and report problems
	tox -e typecheck

.PHONY: workflows-models
workflows-models: ## Generate the Workflows models portion of Argo Workflows
	@datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/workflows/models \
		--base-class hera.workflows._base_model.BaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix
	@python scripts/models.py $(OPENAPI_SPEC_URL) workflows
	@$(MAKE) format

.PHONY: events-models
events-models: ## Generate the Events models portion of Argo Workflows
	@datamodel-codegen \
		--url $(OPENAPI_SPEC_URL) \
		--snake-case-field \
		--target-python-version 3.7 \
		--output src/hera/events/models \
		--base-class hera.events._base_model.BaseModel \
		--wrap-string-literal \
		--disable-appending-item-suffix
	@python scripts/models.py $(OPENAPI_SPEC_URL) events
	@$(MAKE) format

models: ## Generate all the Argo Workflows models
	$(MAKE) workflows-models
	$(MAKE) events-models

.PHONY: workflows-service
workflows-service:  ## Generate the Workflows service option of Hera
	@python scripts/service.py $(OPENAPI_SPEC_URL) workflows
	$(MAKE) format

.PHONY: events-service
events-service:  ## Generate the events service option of Hera
	@python scripts/service.py $(OPENAPI_SPEC_URL) events
	$(MAKE) format

.PHONE: service
services:  ## Generate the services of Hera
	$(MAKE) workflows-service
	$(MAKE) events-service
