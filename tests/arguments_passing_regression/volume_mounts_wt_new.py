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
    use_func_params_in_call=True,
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
        Volume(name="v1", mount_path="/mnt/v1", size="1Gi"),
        Volume(name="v2", mount_path="/mnt/v2", size="3Gi"),
        Volume(name="v3", mount_path="/mnt/v3", size="5Gi"),
    ],
) as w:
    with DAG(name="d"):
        foo("v1").with_(name="v1")
        foo("v2").with_(name="v2")
        foo("v3").with_(name="v3")
