import pytest
from unittest import mock
from hera import ConcurrencyPolicy, CronWorkflow
from argo_workflows.models import IoArgoprojWorkflowV1alpha1CronWorkflow, IoArgoprojWorkflowV1alpha1CronWorkflowSpec, \
    ObjectMeta


class TestConcurrencyPolicy:
    def test_str_returns_expected_value(self):
        assert str(ConcurrencyPolicy.Allow) == "Allow"
        assert str(ConcurrencyPolicy.Replace) == "Replace"
        assert str(ConcurrencyPolicy.Forbid) == "Forbid"
        assert len(ConcurrencyPolicy) == 3


class TestCronWorkflow:
    def test_init_raises_upon_invalid_timezone(self, schedule, setup):
        with pytest.raises(ValueError) as e:
            CronWorkflow('test', schedule, timezone='test')
        assert str(e.value) == "test is not a valid timezone"

    def test_init_adds_expected_fields(self, schedule, setup):
        with CronWorkflow('test', schedule, timezone='America/New_York', starting_deadline_seconds=42,
                          concurrency_policy=ConcurrencyPolicy.Allow) as cw:
            assert cw.schedule == '* * * * *'
            assert cw.timezone == 'America/New_York'
            assert cw.starting_deadline_seconds == 42
            assert cw.concurrency_policy == 'Allow'

    def test_build_returns_expected_workflow(self, schedule, setup):
        with CronWorkflow('test', schedule, timezone='America/New_York', starting_deadline_seconds=42,
                          concurrency_policy=ConcurrencyPolicy.Allow) as w:
            cw = w.build()
            assert isinstance(cw, IoArgoprojWorkflowV1alpha1CronWorkflow)
            assert hasattr(cw, 'metadata')
            assert isinstance(cw.metadata, ObjectMeta)
            assert hasattr(cw, 'spec')
            assert isinstance(cw.spec, IoArgoprojWorkflowV1alpha1CronWorkflowSpec)
            assert hasattr(cw.spec, 'schedule')
            assert cw.spec.schedule == '* * * * *'
            assert hasattr(cw.spec, 'workflow_spec')
            assert hasattr(cw.spec, 'workflow_metadata')
            assert hasattr(cw.spec, 'concurrencyPolicy')
            assert cw.spec.concurrencyPolicy == 'Allow'
            assert hasattr(cw.spec, 'startingDeadlineSeconds')
            assert cw.spec.startingDeadlineSeconds == 42
            assert hasattr(cw.spec, 'timezone')
            assert cw.spec.timezone == 'America/New_York'

    def test_create_calls_service_create(self, schedule, setup):
        with CronWorkflow('test', schedule) as cw:
            cw.service = mock.Mock()
        result = cw.create()
        assert isinstance(result, CronWorkflow)
        cw.service.create_cron_workflow.assert_called_once_with(cw.build())

        cw = CronWorkflow('test', schedule)
        cw.service = mock.Mock()
        with pytest.raises(ValueError) as e:
            cw.in_context = True
            cw.create()
        cw.service.create_cron_workflow.assert_not_called()
        assert str(e.value) == "Cannot invoke `create` when using a Hera context"
