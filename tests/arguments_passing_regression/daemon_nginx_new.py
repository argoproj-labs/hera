from hera.workflows import (
    Container,
    Parameter,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="daemon-nginx-",
    entrypoint="daemon-nginx-example",
) as w:
    nginx_server = Container(
        name="nginx-server",
        daemon=True,
        image="nginx:1.13",
        readiness_probe=m.Probe(
            http_get=m.HTTPGetAction(
                path="/",
                port=80,
            ),
            initial_delay_seconds=2,
            timeout_seconds=1,
        ),
    )
    nginx_client = Container(
        name="nginx-client",
        inputs=Parameter(name="server-ip"),
        image="appropriate/curl:latest",
        command=["/bin/sh", "-c"],
        args=[
            "echo curl --silent -G http://{{inputs.parameters.server-ip}}:80/ && curl "
            "--silent -G http://{{inputs.parameters.server-ip}}:80/"
        ],
        use_func_params_in_call=True,
    )
    with Steps(name="daemon-nginx-example"):
        s = nginx_server()
        nginx_client(s.ip)
