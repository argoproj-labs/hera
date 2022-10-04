"""
This example showcases the classic diamond workflow along with metrics used to track the workflow. For information on
how to use metrics and what metrics are accessible out of the box with Argo see:
https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
"""
from hera import Metric, Task, Workflow


def say(message: str):
    print(message)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("diamond", metrics=[Metric("w", "help-w")]) as w:
    a = Task("a", say, ["This is task A!"], metrics=[Metric("a", "help-a")])
    b = Task("b", say, ["This is task B!"], metrics=[Metric("b", "help-b")])
    c = Task("c", say, ["This is task C!"])
    d = Task("d", say, ["This is task D!"])

    a >> [b, c] >> d

w.create()
