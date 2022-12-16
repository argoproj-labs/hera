# Lint

This example showcases how to lint workflows supported by Hera

```python
from hera import CronWorkflow, Task, Workflow, WorkflowTemplate


def say(msg: str) -> None:
    print(msg)


with Workflow('test-w') as w:
    Task('say', say, with_param=['Hello, world!'])

w.lint()

with CronWorkflow('cron-test-w', '* * * * *') as cw:
    Task('say', say, with_param=['Hello, world!'])

cw.lint()

with WorkflowTemplate('test-wt', labels={'a': 'b'}) as wt:
    Task('say', say, with_param=['Hello, world!'])

wt.lint()
```
