from hera.workflows import (
    DAG,
    Parameter,
    Volume,
    WorkflowTemplate,
    models as m,
    script,
)


@script(
    inputs=Parameter(name="vol"),
    volume_mounts=[m.VolumeMount(name="{{inputs.parameters.vol}}", mount_path="/mnt/vol")],
)
def foo():
    import os
    import subprocess

    print(os.listdir("/mnt"))
    print(subprocess.run("cd /mnt && df -h", shell=True, capture_output=True).stdout.decode())


with WorkflowTemplate(
    generate_name="volumes-",
    entrypoint="d",
    volumes=[
        Volume(name="v1", size="1Gi"),
        Volume(name="v2", size="3Gi"),
        Volume(name="v3", size="5Gi"),
    ],
) as w:
    with DAG(name="d"):
        foo(name="v1", arguments=Parameter(name="vol", value="v1"))
        foo(name="v2", arguments=Parameter(name="vol", value="v2"))
        foo(name="v3", arguments=Parameter(name="vol", value="v3"))
