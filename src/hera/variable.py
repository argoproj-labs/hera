from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Parameter,
)
from pydantic import BaseModel

from hera.env import EnvSpec


class Variable(BaseModel):
    """This allows passing variable into a Task.

    Parameters
    ----------
    name: str
        The name of the variable available inside the Task.
    value: str
        The value to be set for the variable.
    """

    name: str
    value: str

    def get_argument_parameter(self):
        return IoArgoprojWorkflowV1alpha1Parameter(name=self.name, value=self.value)

    def get_input_parameter(self):
        return IoArgoprojWorkflowV1alpha1Inputs(name=self.name)


class VariableAsEnv(Variable):
    """This allows passing information into a Task from another Task, as an environment variables.
    As an example, you can pass a secondary Tasks IP address, to the Task.

    Parameters
    ----------
    name: str
        The name of the environment variable abailable inside the Task.
    value: str
        The value to be set for the environment variable. This could be something like Task.ip

    Notes
    -----
        If you use template_ref in Task, you don't need to use VariableAsEnv, just use Variable.
        VariableAsEnv is for ScriptTemplate or Container.
    """

    def get_env_spec(self):
        return EnvSpec(name=self.name, value=f"{{{{inputs.parameters.{self.name}}}}}")
