from hera.workflows import RetryStrategy, Workflow, script


@script(image="python:alpine3.6", retry_strategy=RetryStrategy(limit=10), add_cwd_to_sys_path=False)
def retry_script():
    import random
    import sys

    exit_code = random.choice([0, 1, 1])
    sys.exit(exit_code)


with Workflow(generate_name="retry-script-", entrypoint="retry-script") as w:
    retry_script()
