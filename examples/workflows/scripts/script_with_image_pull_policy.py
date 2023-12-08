from hera.workflows import Workflow, script
from hera.workflows.models import ImagePullPolicy


@script(image_pull_policy=ImagePullPolicy.always)
def task_with_image_pull_policy():
    print("ok")


with Workflow(generate_name="script-with-image-pull-policy-", entrypoint="task-with-image-pull-policy") as w:
    task_with_image_pull_policy()

w.to_yaml()