from unittest import mock

import pytest
from argo_workflows.models import IoArgoprojWorkflowV1alpha1WorkflowTemplate

from hera import WorkflowTemplate


class TestWorkflowTemplate:
    def test_build_returns_expected_spec(self, setup):
        with WorkflowTemplate("test") as wt:
            template = wt.build()
            assert isinstance(template, IoArgoprojWorkflowV1alpha1WorkflowTemplate)
            assert hasattr(template, "api_version")
            assert template.api_version == "argoproj.io/v1alpha1"
            assert isinstance(template.api_version, str)
            assert hasattr(template, "kind")
            assert isinstance(template.kind, str)
            assert template.kind == "WorkflowTemplate"

    def test_create_calls_service_create(self, setup):
        with WorkflowTemplate("test") as wt:
            with pytest.raises(ValueError) as e:
                wt.create()
            assert str(e.value) == "Cannot invoke `create` when using a Hera context"

        with WorkflowTemplate("test") as wt:
            wt.dag = None
            with pytest.raises(ValueError) as e:
                wt.create()

        with WorkflowTemplate("test") as wt:
            wt.service = mock.Mock()
        wt.create()
        wt.service.create_workflow_template.assert_called_once()

    def test_update_calls_service_update(self, setup):
        with WorkflowTemplate("test") as wt:
            wt.service = mock.Mock()
        wt.update()
        wt.service.update_workflow_template.assert_called_once()

    def test_update_cals_service_delete(self, setup):
        s = mock.Mock()
        with WorkflowTemplate("test", service=s) as wt:
            wt.delete()
        wt.service.delete_workflow_template.assert_called_once()

    def test_lint(self):
        service = mock.Mock()
        service.lint_workflow_template = mock.Mock()
        with WorkflowTemplate("w", service=service) as w:
            w.lint()
        w.service.lint_workflow_template.assert_called_once_with(w.build())
