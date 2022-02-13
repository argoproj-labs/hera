"""Holds input model specifications"""
from typing import List

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Parameter,
)
from pydantic import BaseModel

from hera.env import EnvSpec


class InputFrom(BaseModel):
    """A representation of input from one task to another.

    This is typically used on a task definition to represent the task another task is supposed to take input from and
    what parameters ought to be set by the output.

    name: str
        The name of the task to take input from. The task's results are expected via stdout. Specifically, the task is
        expected to perform the script illustrated in Examples.
    parameters: List[str]
        The list of parameter names to provide as input to the existing task.

    Examples
    --------
    This is a potential task definition:

    from hera.task import Task
    from hera.workflow import Workflow
    from hera.input import InputFrom

    def generate():
        import json
        import sys

        json.dump([{'seconds': 5} for _ in range(10)], sys.stdout)

    def sleep(seconds: int, sentence: str = 'Hello, world!'):
        import time

        print(sentence)
        time.sleep(seconds)

    w = Workflow('fv-testing')
    g = Task('generate', generate)
    s = Task('sleep', sleep, input_from=InputFrom(name='generate', parameters=['seconds']))

    g.next(s)
    w.add_tasks(g, s, a, m, ms)

    w.submit()
    """

    name: str
    parameters: List[str]


class InputParameterAsEnv(BaseModel):
    name: str
    value: str

    def get_argument_parameter(self):
        return IoArgoprojWorkflowV1alpha1Parameter(name=self.name, value=self.value)

    def get_input_parameter(self):
        return IoArgoprojWorkflowV1alpha1Inputs(name=self.name)

    def get_env_spec(self):
        return EnvSpec(name=self.name, value=f"{{{{inputs.parameters.{self.name}}}}}")
