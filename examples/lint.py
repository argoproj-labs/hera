"""This example showcases how to lint workflows supported by Hera"""

from hera import CronWorkflow, Task, Workflow, WorkflowMetadata, WorkflowTemplate


def say(msg: str) -> None:
    print(msg)


with Workflow("test-w") as w:
    Task("say", say, with_param=["Hello, world!"])

w.lint()

with CronWorkflow("cron-test-w", "* * * * *") as cw:
    Task("say", say, with_param=["Hello, world!"])

cw.lint()

with WorkflowTemplate("test-wt", workflow_metadata=WorkflowMetadata(labels={"a": "b"})) as wt:
    Task("say", say, with_param=["Hello, world!"])

wt.lint()
