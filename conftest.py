from typing import Dict, List, Tuple

import pytest
from pydantic import BaseModel

from hera.artifact import InputArtifact, OutputArtifact
from hera.cron_workflow import CronWorkflow
from hera.cron_workflow_service import CronWorkflowService
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


@pytest.fixture(scope='session')
def ws():
    yield WorkflowService(host='https://abc.com', token='abc')


@pytest.fixture(scope='function')
def w(ws):
    yield Workflow('w', service=ws)


@pytest.fixture(scope='function')
def cws():
    yield CronWorkflowService(host='https://abc.com', token='abc')


@pytest.fixture(scope='session')
def schedule():
    yield "* * * * *"


@pytest.fixture(scope='function')
def cw(cws, schedule):
    yield CronWorkflow('cw', schedule, service=cws)


@pytest.fixture(scope='session')
def in_artifact():
    yield InputArtifact(name='test', path='/test', from_task='test-o', artifact_name='test-o')


@pytest.fixture(scope='session')
def out_artifact():
    yield OutputArtifact(name='test', path='/test')


@pytest.fixture(scope='session')
def mock_model():
    class MockModel(BaseModel):
        field1: int = 1
        field2: int = 2

    yield MockModel


@pytest.fixture(scope='session')
def no_op():
    def _no_op():
        pass

    yield _no_op


@pytest.fixture(scope='session')
def op():
    def _op(a):
        print(a)

    yield _op


@pytest.fixture(scope='session')
def kwarg_op():
    def _kwarg_op(a: int = 42):
        print(a)

    yield _kwarg_op


@pytest.fixture(scope='session')
def kwarg_multi_op():
    def _kwarg_multi_op(a: int = 42, b: int = 43):
        print(a, b)

    yield _kwarg_multi_op


@pytest.fixture(scope='session')
def multi_op():
    def _multi_op(a, b, c):
        print(a, b, c)

    yield _multi_op


@pytest.fixture(scope='session')
def typed_op():
    def _typed_op(a) -> List[Dict[str, Tuple[int, int]]]:
        print(a)
        return [{'a': (a, a)}]

    yield _typed_op


@pytest.fixture(scope='session')
def long_op():
    def _long_op(
        very_long_parameter_name,
        very_very_long_parameter_name,
        very_very_very_long_parameter_name,
        very_very_very_very_long_parameter_name,
        very_very_very_very_very_long_parameter_name,
    ):
        print(42)

    yield _long_op
