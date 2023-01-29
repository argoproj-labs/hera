# Workflow With Custom Image

This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera

```python
from hera import ImagePullPolicy, Task, Workflow

with Workflow("pipeline-image-testing") as w:
    # This can be used when you have your own custom image
    # Image_pull_policy is set to Never because on localhost when you test
    # you don't need to pull the image
    Task(
        "workflow-with-custom-image",
        image="my-custom-image-name:latest",
        image_pull_policy=ImagePullPolicy.never,
        command=["python", "-m", "src.pipeline_example"],
    )

w.create()
```
