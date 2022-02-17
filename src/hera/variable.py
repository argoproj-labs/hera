from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Parameter,
)
from pydantic import BaseModel

from hera.env import EnvSpec


class VariableAsEnv(BaseModel):
    """This allows passing information into a Task from another Task, as an environment variables.
    As an example, you can pass a secondary Tasks IP address, to the Task.

    Parameters
    ----------
    name: str
        The name of the environment variable abailable inside the Task.
    value: str
        The value to be set for the environment variable. This could be something like Task.ip
    """

    name: str
    value: str

    def get_argument_parameter(self):
        return IoArgoprojWorkflowV1alpha1Parameter(name=self.name, value=self.value)

    def get_input_parameter(self):
        return IoArgoprojWorkflowV1alpha1Inputs(name=self.name)

    def get_env_spec(self):
        return EnvSpec(name=self.name, value=f"{{{{inputs.parameters.{self.name}}}}}")
