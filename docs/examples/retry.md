# Retry

This example showcases how to set a retry on a task. The retry will make the task back off for 5 seconds
post-failure and allow the retries to occur over a duration of 60 seconds.

```python
from hera import Backoff, RetryStrategy, Task, Workflow


def random_fail():
    import random

    p = random.random()
    if p < 0.5:
        raise Exception("p < .5 = success")
    print("p >= .5 = success")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("retry") as w:
    Task("fail", random_fail, retry_strategy=RetryStrategy(backoff=Backoff(duration="5", max_duration="60")))

w.create()

```