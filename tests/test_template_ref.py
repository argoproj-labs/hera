from argo_workflows.models import IoArgoprojWorkflowV1alpha1TemplateRef

from hera import TemplateRef


def test_template_ref_has_expected_argo_spec():
    t = TemplateRef(name="workflow-template", template="template").argo_spec

    assert isinstance(t, IoArgoprojWorkflowV1alpha1TemplateRef)
    assert t.name == "workflow-template"
    assert t.template == "template"
