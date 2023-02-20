"""
This example showcases how Hera can dynamically set environmental variables
"""

from hera.workflows import ConfigMapEnvFrom, Env, Parameter, Task, Workflow


def inspect_envs():
    import os

    print(os.environ)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("test-env-variables", parameters=[Parameter("env-value", "wf-env-value")]) as wf:
    Task(
        "test-env",
        inspect_envs,
        env=[
            Env(name="FIXED_ENV", value="fixed-env-value"),
            Env(name="WF_ENV", value_from_input=wf.get_parameter("env-value")),
            ConfigMapEnvFrom(
                config_map_name="<your-reference>"
            ),  # Assumes the user has a config map in the k8s cluster
        ],
    )

wf.create()
