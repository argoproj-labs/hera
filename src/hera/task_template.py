from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from hera.artifact import Artifact
from hera.input import InputFrom
from hera.task import Task


class TaskTemplate(Task):
    def task(
        self,
        name: str = None,
        func_params: Optional[List[Dict[str, Union[int, str, float, dict, BaseModel]]]] = None,
        input_from: Optional[InputFrom] = None,
        input_artifacts: Optional[List[Artifact]] = None,
    ) -> Task:
        task = Task(
            name=self.name,
            func=self.func,
            func_params=func_params or self.func_params,
            input_from=input_from or self.input_from,
            input_artifacts=input_artifacts or self.input_artifacts,
            output_artifacts=self.output_artifacts,
            image=self.image,
            image_pull_policy=self.image_pull_policy,
            daemon=self.daemon,
            command=self.command,
            args=self.args,
            # Envs provided by assignigning to Task object.
            resources=self.resources,
            working_dir=self.working_dir,
            retry=self.retry,
            tolerations=self.tolerations,
            node_selectors=self.node_selector,
            labels=self.labels,
            annotations=self.annotations,
            variables=self.variables,
            security_context=self.security_context,
            continue_on_fail=self.continue_on_fail,
            continue_on_error=self.continue_on_error,
            template_ref=self.template_ref,
        )
        name = name or self.name
        task.name = name.replace("_", "-")  # RFC1123
        task.env_from = self.env_from
        task.env = self.env
        task.argo_template = self.argo_template

        # Reload task spec with reused template.
        task.argo_task = task.get_task_spec()
        return task
