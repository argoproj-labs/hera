"""This example showcases how one can run an Nginx sidecar container with Hera"""

from hera.workflows import Container, UserContainer, Workflow

with Workflow(generate_name="sidecar-nginx-", entrypoint="sidecar-nginx-example") as w:
    Container(
        name="sidecar-nginx-example",
        image="appropriate/curl",
        command=["sh", "-c"],
        args=["until `curl -G 'http://127.0.0.1/' >& /tmp/out`; do echo sleep && sleep 1; done && cat /tmp/out"],
        sidecars=UserContainer(name="nginx", image="nginx:1.13", command=["nginx", "-g", "daemon off;"]),
    )
