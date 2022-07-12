import pytest
from argo_workflows.exceptions import ApiAttributeError
from argo_workflows.models import IoArgoprojWorkflowV1alpha1ResourceTemplate

from hera import ResourceTemplate


@pytest.fixture
def action():
    yield "create"


@pytest.fixture
def failure_condition():
    yield "status,phase in (Failed, Error)"


@pytest.fixture
def success_condition():
    yield "status.phase == Succeeded"


@pytest.fixture
def manifest():
    yield """
        apiVersion: argoproj.io/v1alpha1
        kind: Workflow
        metadata:
          generateName: hello-world-
        spec:
          entrypoint: say-hello
          templates:
            - name: say-hello
            container:
              image: alpine
              command: ["echo"]
              args: ["hello world"]
              resources:
                limits:
                  memory: 32Mi
                  cpu: 100m
    """


@pytest.fixture
def merge_strategy():
    yield "strategic"


@pytest.fixture
def set_owner_reference():
    yield False


def test_resource_template_init(
    action, manifest, failure_condition, success_condition, merge_strategy, set_owner_reference
):
    resource_template = ResourceTemplate(
        action=action,
        manifest=manifest,
        failure_condition=failure_condition,
        success_condition=success_condition,
        merge_strategy=merge_strategy,
        set_owner_reference=set_owner_reference,
    )

    assert resource_template.action == action
    assert resource_template.manifest == manifest
    assert resource_template.failure_condition == failure_condition
    assert resource_template.success_condition == success_condition
    assert resource_template.merge_strategy == merge_strategy
    assert resource_template.set_owner_reference == set_owner_reference
    assert resource_template.flags is None


def test_get_resource_template(
    action, manifest, failure_condition, success_condition, merge_strategy, set_owner_reference
):
    resource_template = ResourceTemplate(
        action=action,
        manifest=manifest,
        failure_condition=failure_condition,
        success_condition=success_condition,
        merge_strategy=merge_strategy,
        set_owner_reference=set_owner_reference,
    )

    resource = resource_template.get_resource_template()
    assert isinstance(resource, IoArgoprojWorkflowV1alpha1ResourceTemplate)
    assert resource.action == action
    assert resource.manifest == manifest
    assert resource.failure_condition == failure_condition
    assert resource.success_condition == success_condition
    assert resource.merge_strategy == merge_strategy
    assert resource.set_owner_reference == set_owner_reference
    assert resource_template.flags is None
    with pytest.raises(ApiAttributeError):
        resource.flags
