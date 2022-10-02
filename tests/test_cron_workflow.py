from unittest import mock

import pytest
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1CronWorkflow,
    IoArgoprojWorkflowV1alpha1CronWorkflowSpec,
    ObjectMeta,
)

from hera import ConcurrencyPolicy, CronWorkflow


class TestConcurrencyPolicy:
    def test_str_returns_expected_value(self):
        assert str(ConcurrencyPolicy.Allow) == "Allow"
        assert str(ConcurrencyPolicy.Replace) == "Replace"
        assert str(ConcurrencyPolicy.Forbid) == "Forbid"
        assert len(ConcurrencyPolicy) == 3


class TestCronWorkflow:
    def test_init_raises_upon_invalid_timezone(self, schedule, setup):
        with pytest.raises(ValueError) as e:
            CronWorkflow("test", schedule, timezone="test")
        assert str(e.value) == "test is not a valid timezone"

    def test_init_adds_expected_fields(self, schedule, setup):
        with CronWorkflow(
            "test",
            schedule,
            timezone="America/New_York",
            starting_deadline_seconds=42,
            concurrency_policy=ConcurrencyPolicy.Allow,
        ) as cw:
            assert cw.schedule == "* * * * *"
            assert cw.timezone == "America/New_York"
            assert cw.starting_deadline_seconds == 42
            assert cw.concurrency_policy == "Allow"

    def test_build_returns_expected_workflow(self, schedule, setup):
        with CronWorkflow(
            "test",
            schedule,
            timezone="America/New_York",
            starting_deadline_seconds=42,
            concurrency_policy=ConcurrencyPolicy.Allow,
        ) as w:
            cw = w.build()
            assert isinstance(cw, IoArgoprojWorkflowV1alpha1CronWorkflow)
            assert hasattr(cw, "metadata")
            assert isinstance(cw.metadata, ObjectMeta)
            assert hasattr(cw, "spec")
            assert isinstance(cw.spec, IoArgoprojWorkflowV1alpha1CronWorkflowSpec)
            assert hasattr(cw.spec, "schedule")
            assert cw.spec.schedule == "* * * * *"
            assert hasattr(cw.spec, "workflow_spec")
            assert hasattr(cw.spec, "workflow_metadata")
            assert hasattr(cw.spec, "concurrencyPolicy")
            assert cw.spec.concurrencyPolicy == "Allow"
            assert hasattr(cw.spec, "startingDeadlineSeconds")
            assert cw.spec.startingDeadlineSeconds == 42
            assert hasattr(cw.spec, "timezone")
            assert cw.spec.timezone == "America/New_York"

    def test_create_calls_service_create(self, schedule, setup):
        with CronWorkflow("test", schedule) as cw:
            cw.service = mock.Mock()
            cw.service.create_cron_workflow = mock.Mock()
        result = cw.create()
        assert isinstance(result, CronWorkflow)
        cw.service.create_cron_workflow.assert_called_once_with(cw.build())

        cw = CronWorkflow("test", schedule)
        cw.service = mock.Mock()
        cw.service.create_cron_workflow = mock.Mock()
        with pytest.raises(ValueError) as e:
            cw.in_context = True
            cw.create()
        cw.service.create_cron_workflow.assert_not_called()
        assert str(e.value) == "Cannot invoke `create` when using a Hera context"

    def test_delete_calls_service_delete(self, schedule, setup):
        with CronWorkflow("cw", schedule) as cw:
            cw.service = mock.Mock()
            cw.service.delete_workflow = mock.Mock()
        result = cw.delete()
        assert isinstance(result, CronWorkflow)
        cw.service.delete_workflow.assert_called_once()

    def test_delete_calls_service_suspend(self, schedule, setup):
        with CronWorkflow("cw", schedule) as cw:
            cw.service = mock.Mock()
            cw.service.suspend_cron_workflow = mock.Mock()
        cw.suspend()
        cw.service.suspend_cron_workflow.assert_called_once()

    def test_delete_calls_service_resume(self, schedule, setup):
        with CronWorkflow("cw", schedule) as cw:
            cw.service = mock.Mock()
            cw.service.resume_cron_workflow = mock.Mock()
        cw.resume()
        cw.service.resume_cron_workflow.assert_called_once()

    def test_update_adds_expected_fields_to_cw_self(self, schedule, setup):
        with CronWorkflow("cw", schedule) as cw:
            cw.service = mock.Mock()
            get_cron_return = mock.Mock()
            get_cron_return.metadata = {'resourceVersion': '42', 'uid': '42'}
            cw.service.get_cron_workflow = mock.Mock(return_value=get_cron_return)
            cw.service.update_cron_workflow = mock.Mock()
        cw.update()
        cw.service.get_cron_workflow.assert_called_once()
