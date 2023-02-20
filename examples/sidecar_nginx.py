"""This example showcases how one can run an Nginx sidecar container with Hera"""

from hera.workflows import Sidecar, Task, Workflow

# this assumes you have set a global token and a global host
with Workflow("sidecar-nginx-", generate_name=True) as w:
    Task(
        "sidecar-nginx-example",
        image="appropriate/curl",
        command=["sh", "-c"],
        args=["until `curl -G 'http://127.0.0.1/' >& /tmp/out`; do echo sleep && sleep 1; done && cat /tmp/out"],
        sidecars=[Sidecar("nginx", image="nginx:1.13", command=["nginx", "-g", "daemon off;"])],
    )

w.create()
