"""This example showcases how to lint workflows supported by Hera"""

from hera import CronWorkflow, Task, Workflow, WorkflowMetadata, WorkflowTemplate


def say(msg: str) -> None:
    print(msg)


with Workflow(generate_name="test-w-") as w:
    Task("say", say, with_param=["Hello, world!"])

w.lint()

with WorkflowTemplate(generate_name="test-wt-", workflow_metadata=WorkflowMetadata(labels={"a": "b"})) as wt:
    Task("say", say, with_param=["Hello, world!"])

wt.lint()

with CronWorkflow("cron-test-w", "* * * * *") as cw:
    Task("say", say, with_param=["Hello, world!"])

cw.lint()
