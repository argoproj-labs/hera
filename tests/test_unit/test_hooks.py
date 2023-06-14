from hera.shared import global_config, register_pre_build_hook
from hera.workflows.cluster_workflow_template import ClusterWorkflowTemplate
from hera.workflows.container import Container
from hera.workflows.workflow import Workflow
from hera.workflows.workflow_template import WorkflowTemplate


def test_container_pre_build_hooks():
    @register_pre_build_hook
    def set_container_default_image(container: Container) -> Container:
        container.image = "test_image"
        return container

    with Workflow(name="t") as w:
        c = Container()

    assert c.image == "python:3.8"
    w.build()
    assert c.image == "test_image"
    global_config.reset()

    @register_pre_build_hook
    def set_container_label(container: Container) -> Container:
        container.labels = {"test": "test"}
        return container

    register_pre_build_hook(set_container_default_image)

    with Workflow(name="t") as w:
        c = Container()

    assert c.image == "python:3.8"
    assert c.labels is None
    w.build()
    assert c.image == "test_image"
    assert c.labels["test"] == "test"
    global_config.reset()


def test_workflow_pre_build_hooks():
    @register_pre_build_hook
    def set_workflow_default_node_selector(workflow: Workflow) -> Workflow:
        workflow.node_selector = {
            "domain": "test",
            "team": "ABC",
        }
        return workflow

    with Workflow(name="t") as w:
        pass

    assert w.node_selector is None
    w.build()
    assert w.node_selector["domain"] == "test"
    assert w.node_selector["team"] == "ABC"
    global_config.reset()

    register_pre_build_hook(set_workflow_default_node_selector)

    @register_pre_build_hook
    def set_workflow_default_labels(workflow: Workflow) -> Workflow:
        workflow.labels = {
            "label": "test",
        }
        return workflow

    with Workflow(name="t") as w:
        pass

    assert w.node_selector is None
    assert w.labels is None
    w.build()
    assert w.node_selector["domain"] == "test"
    assert w.node_selector["team"] == "ABC"
    assert w.labels["label"] == "test"
    global_config.reset()


def test_workflow_template_pre_build_hooks():
    global_config.reset()

    @register_pre_build_hook
    def set_workflow_template_default_labels(workflow_template: WorkflowTemplate) -> WorkflowTemplate:
        workflow_template.labels = {
            "wt_label": "test",
        }
        return workflow_template

    @register_pre_build_hook
    def set_cwt_default_labels(cluster_workflow_template: ClusterWorkflowTemplate) -> ClusterWorkflowTemplate:
        cluster_workflow_template.labels = {
            "cwt_label": "test",
        }
        return cluster_workflow_template

    with WorkflowTemplate(name="t") as wt:
        pass

    assert wt.labels is None
    wt.build()
    assert wt.labels == {"wt_label": "test"}


def test_cluster_workflow_template_pre_build_hooks():
    global_config.reset()

    @register_pre_build_hook
    def set_workflow_template_default_labels(workflow_template: WorkflowTemplate) -> WorkflowTemplate:
        workflow_template.labels = {
            "wt_label": "test",
        }
        return workflow_template

    @register_pre_build_hook
    def set_cwt_default_labels(cluster_workflow_template: ClusterWorkflowTemplate) -> ClusterWorkflowTemplate:
        cluster_workflow_template.labels = {
            "cwt_label": "test",
        }
        return cluster_workflow_template

    with ClusterWorkflowTemplate(name="t") as cwt:
        pass

    assert cwt.labels is None
    cwt.build()
    assert cwt.labels == {"cwt_label": "test"}
