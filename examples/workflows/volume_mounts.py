from hera.workflows import Workflow, DAG, script, Volume, models as m, Parameter


@script(inputs=Parameter(name="vol"), volume_mounts=[m.VolumeMount(name="{{inputs.parameters.vol}}", mount_path="/mnt/vol")])
def foo():
    import os
    import subprocess
    print(os.listdir("/mnt"))
    print(subprocess.run("df -h /mnt", shell=True, capture_output=True).stdout.decode())
    import time
    time.sleep(300)


with Workflow(generate_name="volumes-", entrypoint="d", volumes=[
    Volume(name="v1", mount_path="/mnt/v1", size="1Gi"),
    Volume(name="v2", mount_path="/mnt/v2", size="3Gi"),
    Volume(name="v3", mount_path="/mnt/v3", size="5Gi"),
]) as w:
    with DAG(name="d"):
        foo(name="v1", arguments=Parameter(name="vol", value="v1"))
        foo(name="v2", arguments=Parameter(name="vol", value="v2"))
        foo(name="v3", arguments=Parameter(name="vol", value="v3"))

w.create()
