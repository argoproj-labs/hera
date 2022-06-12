"""This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera"""
from hera import ImagePullPolicy, Task, Workflow, WorkflowService

# TODO: replace the domain and token with your own
ws = WorkflowService(host='', verify_ssl=False, token='')
w = Workflow('pipeline-image-testing', ws, namespace="argo")

# This can be used when you have your own custom image
# Image_pull_policy is set to Never because on localhost when you test
# you don't need to pull the image
t = Task(
    'workflow-with-custom-image',
    image='my-custom-image-name:latest',
    image_pull_policy=ImagePullPolicy.Never,
    command=["python", "-m", "src.pipeline_example"],
)

w.add_task(t)
w.create()
