import asyncio
import importlib
import random
import time

import pytest
import requests

from hera.exceptions import HeraException
from hera.workflows.async_service import AsyncWorkflowsService
from hera.workflows.cluster_workflow_template import ClusterWorkflowTemplate
from hera.workflows.cron_workflow import CronWorkflow
from hera.workflows.models import Workflow as ModelWorkflow
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow import Workflow
from hera.workflows.workflow_template import WorkflowTemplate
from tests.test_examples import CI_MODE, _get_examples

# Skip long-running and unsupported examples
TIME_LIMIT_SECONDS = 120
SKIP_LINT_EXAMPLES = {
    "new_decorators_auto_template_refs",  # Uses TemplateRefs to non-existent WorkflowTemplates
    "template_refs",  # Also uses TemplateRefs - the WorkflowTemplates are in the file though
    "parquet_pandas",
}
SKIP_SUBMISSION_EXAMPLES = SKIP_LINT_EXAMPLES.union(
    {
        "artifact_loaders",
        "conditional_on_task_status",
        "container_set_with_env",
        "create_volume_for_workflow",
        "cron_hello_world",
        "cron_workflow_stop_strategy",
        "custom_serialiser",
        "dag_input_output",
        "dask",
        "data",
        "dynamic_fanout_container",
        "env",
        "env_from",
        "fine_tune_llama",
        "global_config",
        "http",
        "init_containers_with_env",
        "map_reduce",
        "new_dag_decorator_artifacts",
        "new_dag_decorator_inner_dag",
        "new_dag_decorator_params",
        "new_decorators_auto_template_refs",
        "new_decorators_basic_script",
        "new_decorators_fanout_loop",
        "new_steps_decorator_with_parallel_steps",
        "recursive_dag",
        "recursive_steps",
        "resource_flags",
        "retry_workflow",
        "runner_artifacts",
        "script_runner_io",
        "spacy_inference_pipeline",
        "spark",
        "suspend",
        "suspend_input_duration",
        "template_sets",
        "testing_templates_and_workflows",
        "typed_script_input_output",
        "user_container",
        "volume_mount",
        "volume_mounts_nfs",
        "volume_mounts_wt",
        "wandb_ml_monitoring",
        "workflow_of_workflows",
        "workflow_with_global_params",
    }
)


@pytest.fixture
def workflows_service():
    workflows_service = WorkflowsService(
        host="https://localhost:2746",
        namespace="argo",
        verify_ssl=False,
    )
    yield workflows_service


@pytest.fixture
def async_workflows_service():
    workflows_service = AsyncWorkflowsService(
        host="https://localhost:2746",
        namespace="argo",
        verify_ssl=False,
    )
    yield workflows_service


@pytest.mark.on_cluster
@pytest.mark.parametrize(
    "module_name",
    [
        pytest.param(
            module_name,
            marks=pytest.mark.skipif(
                bool(CI_MODE) or filename in SKIP_SUBMISSION_EXAMPLES, reason="Run all examples on local install only"
            ),
            id=filename,
        )
        for _, module_name, filename in _get_examples()
    ],
)
async def test_submission(
    module_name,
    global_config_fixture,
    async_workflows_service: AsyncWorkflowsService,
):
    global_config_fixture.host = "https://localhost:2746"
    workflow = importlib.import_module(module_name).w

    # Skip anything not a Workflow
    if isinstance(workflow, (WorkflowTemplate, ClusterWorkflowTemplate, CronWorkflow)):
        assert False, "Add non-workflow example to 'SKIP_SUBMISSION_EXAMPLES' set"

    assert isinstance(workflow, Workflow)

    # Skip examples using the `runner`
    if "hera.workflows.runner" in workflow.to_yaml():
        assert False, "Add runner example to 'SKIP_SUBMISSION_EXAMPLES' set"

    workflow.namespace = "argo"
    workflow.service_account_name = "argo"
    workflow.workflows_service = async_workflows_service

    now = time.time()

    while True:
        try:
            model_workflow = await workflow.async_create(wait=True, poll_interval=TIME_LIMIT_SECONDS // 3)
        except requests.exceptions.ConnectionError:
            await asyncio.sleep(random.randint(25, 35))
            model_workflow = await workflow.async_create(wait=True, poll_interval=TIME_LIMIT_SECONDS // 3)
            continue
        break

    elapsed = time.time() - now
    assert isinstance(model_workflow, ModelWorkflow)
    assert model_workflow.status
    assert model_workflow.status.phase == "Succeeded"

    assert elapsed < TIME_LIMIT_SECONDS, (
        f"Workflow took longer than {TIME_LIMIT_SECONDS} (but succeeded), consider adding to 'SKIP_SUBMISSION_EXAMPLES' set"
    )


@pytest.mark.on_cluster
@pytest.mark.parametrize(
    "module_name",
    [
        pytest.param(
            module_name,
            marks=pytest.mark.skipif(filename in SKIP_LINT_EXAMPLES, reason="The example doesn't pass linting"),
            id=filename,
        )
        for _, module_name, filename in _get_examples()
    ],
)
async def test_lint(
    module_name,
    global_config_fixture,
    async_workflows_service: WorkflowsService,
):
    global_config_fixture.host = "https://localhost:2746"
    workflow = importlib.import_module(module_name).w

    if not isinstance(workflow, Workflow):
        return

    workflow.namespace = "argo"
    workflow.service_account_name = "argo"
    workflow.workflows_service = async_workflows_service

    try:
        await workflow.async_lint()
    except HeraException as e:
        assert False, f"Workflow failed linting: {e}"
