from hera.workflows import (
    DAG,
    NFSVolume,
    Parameter,
    Workflow,
    models as m,
    script,
)


@script(
    inputs=Parameter(name="vol"),
    volume_mounts=[m.VolumeMount(name="{{inputs.parameters.vol}}", mount_path="/mnt/nfs")],
)
def foo():
    import os
    import subprocess

    print(os.listdir("/mnt"))
    print(subprocess.run("cd /mnt && df -h", shell=True, capture_output=True).stdout.decode())


with Workflow(
    generate_name="volumes-",
    volumes=[NFSVolume(name="nfs-volume", server="your.nfs.server", mount_path="/mnt/nfs", path="/share/nfs")],
    entrypoint="d",
) as w:
    with DAG(name="d"):
        foo(name="v1", arguments=Parameter(name="vol", value="nfs-volume"))
