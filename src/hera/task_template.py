import json
from typing import Optional, List, Dict, Union

from pydantic import BaseModel

from hera.artifact import Artifact
from hera.input import InputFrom
from hera.task import Task
from hera.variable import VariableAsEnv


class TaskTemplate(Task):
    def task(
        self,
        name: str,
        func_params: Optional[
            List[Dict[str, Union[int, str, float, dict, BaseModel]]]
        ] = None,
        input_from: Optional[InputFrom] = None,
        input_artifacts: Optional[List[Artifact]] = None,
    ) -> Task:
        task = Task(
            name=self.name,
            func_params=func_params,
            input_from=input_from,
            input_artifacts=input_artifacts,
        )
        task.name = name.replace("_", "-")  # RFC1123
        task.argo_template = self.argo_template

        task.variables = [
            VariableAsEnv(name=key, value=json.dumps(value))
            for param in func_params
            for key, value in param.items()
        ]
        task.parameters = task.get_parameters()
        task.argo_input_artifacts = task.get_argo_input_artifacts()

        task.arguments = task.get_arguments()
        task.argo_task = task.get_task_spec()
        return task
