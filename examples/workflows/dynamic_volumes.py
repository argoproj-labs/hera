from hera.workflows import DAG, Volume, Workflow, script


@script(volumes=Volume(name="v", size="1Gi", mount_path="/mnt/vol"))
def foo():
    import subprocess

    print(subprocess.run("cd && /mnt && df -h", shell=True, capture_output=True).stdout.decode())


with Workflow(generate_name="dynamic-volumes-", entrypoint="d") as w:
    with DAG(name="d"):
        foo()
