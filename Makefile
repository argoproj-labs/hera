ARGO_WORKFLOWS_VERSION="3.5.5"
OPENAPI_SPEC_URL="https://raw.githubusercontent.com/argoproj/argo-workflows/v$(ARGO_WORKFLOWS_VERSION)/api/openapi-spec/swagger.json"
SPEC_PATH="$(shell pwd)/argo-workflows-$(ARGO_WORKFLOWS_VERSION).json"

.PHONY: help
help: ## Showcase the help instructions for all the available `make` commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Run poetry install with all extras for development
	@poetry env use system
	@poetry install --all-extras

.PHONY: install-3.8
install-3.8: ## Install python3.8 for generating test data
	@poetry env use 3.8
	@poetry install --all-extras

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
	@git diff --exit-code || (echo "Code is not up-to-date. Please run 'make codegen'" && exit 1)

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
	@poetry run python -m pytest --cov-report=term-missing -m "not on_cluster"

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
		--use-annotated \
		--use-default-kwarg
	@find src/hera/workflows/models/ -name '*.py' -exec sed -i.bak 's/from pydantic import Field/from hera.shared._pydantic import Field/' {} +
	@find src/hera/workflows/models/ -name '*.bak' -delete
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) workflows
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
		--use-annotated \
		--use-default-kwarg
	@find src/hera/events/models/ -name '*.py' -exec sed -i.bak 's/from pydantic import Field/from hera.shared._pydantic import Field/' {} +
	@find src/hera/events/models/ -name '*.bak' -delete
	@poetry run python scripts/models.py $(OPENAPI_SPEC_URL) events
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

.PHONY: regenerate-example
regenerate-example:  ## Regenerates the yaml for a single example, using EXAMPLE_FILENAME envvar
regenerate-example: install
	@HERA_REGENERATE=1 poetry run python -m pytest -k $(EXAMPLE_FILENAME)

.PHONY: regenerate-test-data
regenerate-test-data:  ## Regenerates the test data from upstream examples and runs tests, report missing examples
regenerate-test-data: install-3.8
	find examples -name "*.yaml" -type f -delete
	HERA_REGENERATE=1 make test examples
	@poetry run python -m pytest -k test_for_missing_examples --runxfail

.PHONY: install-k3d
install-k3d: ## Install k3d client
	curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

.PHONY: install-argo
install-argo:  ## Install argo client
	# Download the binary
	curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v$(ARGO_WORKFLOWS_VERSION)/argo-linux-amd64.gz

	# Unzip
	gunzip argo-linux-amd64.gz

	# Make binary executable
	chmod +x argo-linux-amd64

	# Move binary to path
	sudo mv ./argo-linux-amd64 /usr/local/bin/argo

	# Test installation
	argo version

.PHONY: run-argo
run-argo: ## Start the argo server
	k3d cluster list | grep test-cluster || k3d cluster create test-cluster
	k3d kubeconfig merge test-cluster --kubeconfig-switch-context
	kubectl get namespace argo || kubectl create namespace argo
	kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v$(ARGO_WORKFLOWS_VERSION)/install.yaml
	kubectl patch deployment argo-server --namespace argo --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": ["server", "--auth-mode=server"]}]'
	kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=argo:default --namespace=argo
	kubectl rollout status -n argo deployment/argo-server --timeout=120s --watch=true

.PHONY: stop-argo
stop-argo:  ## Stop the argo server
	k3d cluster stop test-cluster

.PHONY: test-on-cluster
test-on-cluster: ## Run workflow tests (requires local argo cluster)
	@(kubectl -n argo port-forward deployment/argo-server 2746:2746 &)
	@poetry run python -m pytest tests/submissions -m on_cluster
