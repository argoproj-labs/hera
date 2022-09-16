import random

import pytest
from argo_workflows.model.capabilities import Capabilities
from argo_workflows.model.pod_security_context import PodSecurityContext
from argo_workflows.model.security_context import SecurityContext

from hera import TaskSecurityContext, WorkflowSecurityContext


@pytest.fixture
def privileged():
    yield random.choice([True, False])


@pytest.fixture
def run_as_user():
    yield random.randint(10, 1000)


@pytest.fixture
def run_as_group():
    yield random.randint(10, 1000)


@pytest.fixture
def fs_group():
    yield random.randint(10, 1000)


@pytest.fixture
def run_as_non_root():
    yield random.random() > 0.5


@pytest.fixture
def additional_capabilities():
    yield ["SYS_RAWIO"]


def test_workflow_init_passes(privileged, run_as_user, run_as_group, fs_group, run_as_non_root):
    wsc = WorkflowSecurityContext(
        privileged=privileged,
        run_as_user=run_as_user,
        run_as_group=run_as_group,
        fs_group=fs_group,
        run_as_non_root=run_as_non_root,
    )

    assert wsc.privileged == privileged
    assert wsc.run_as_user == run_as_user
    assert wsc.run_as_group == run_as_group
    assert wsc.fs_group == fs_group
    assert wsc.run_as_non_root == run_as_non_root


def test_workflow_get_security_context(privileged, run_as_user, run_as_group, fs_group, run_as_non_root):
    wsc = WorkflowSecurityContext(
        privileged=privileged,
        run_as_user=run_as_user,
        run_as_group=run_as_group,
        fs_group=fs_group,
        run_as_non_root=run_as_non_root,
    )
    sc = wsc.get_security_context()
    assert isinstance(sc, PodSecurityContext)
    assert sc.privileged == privileged
    assert sc.run_as_user == run_as_user
    assert sc.run_as_group == run_as_group
    assert sc.fs_group == fs_group
    assert sc.run_as_non_root == run_as_non_root


def test_task_init_passes(privileged, run_as_user, run_as_group, run_as_non_root, additional_capabilities):
    sc = TaskSecurityContext(
        privileged=privileged,
        run_as_user=run_as_user,
        run_as_group=run_as_group,
        run_as_non_root=run_as_non_root,
        additional_capabilities=additional_capabilities,
    )

    assert sc.privileged == privileged
    assert sc.run_as_user == run_as_user
    assert sc.run_as_group == run_as_group
    assert sc.run_as_non_root == run_as_non_root
    assert sc.additional_capabilities == additional_capabilities


def test_task_get_security_context(privileged, run_as_user, run_as_group, run_as_non_root, additional_capabilities):
    tsc = TaskSecurityContext(
        privileged=privileged,
        run_as_user=run_as_user,
        run_as_group=run_as_group,
        run_as_non_root=run_as_non_root,
        additional_capabilities=additional_capabilities,
    )
    sc = tsc.build_security_context()
    capabilities = Capabilities(add=additional_capabilities)
    assert isinstance(sc, SecurityContext)
    assert sc.privileged == privileged
    assert sc.run_as_user == run_as_user
    assert sc.run_as_group == run_as_group
    assert sc.run_as_non_root == run_as_non_root
    assert sc.capabilities == capabilities
