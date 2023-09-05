# Advanced Template Features

This section exemplifies `template` features found in Argo, but are beyond the scope of the Walk Through.

## Template-Level Lifecycle Hooks

Lifecycle hooks at the template level are typically used to run a given template, according to a given condition on a
`Step` or `Task`, such as when it has a `Running` or `Succeeded` status.

* [Read more about Lifecycle Hooks on the Argo docs](https://argoproj.github.io/argo-workflows/lifecyclehook/)
* [See the template-level lifecycle hook example](../examples/workflows/upstream/life_cycle_hooks_tmpl_level.md)

## Secrets

To access secrets stored in your Kubernetes/Argo cluster, you should use the `env` or `env_from` members of
`TemplateMixin` (i.e. any standard template).

```py
from hera.workflows import (
    ConfigMapEnv,
    ConfigMapEnvFrom,
    Container,
    Env,
    ResourceEnv,
    SecretEnv,
    SecretEnvFrom,
    Workflow,
)

with Workflow(generate_name="secret-env-from-", entrypoint="whalesay") as w:
    whalesay = Container(
        image="docker/whalesay:latest",
        command=["cowsay"],
        env_from=[
            SecretEnvFrom(prefix="abc", name="secret", optional=False),
            ConfigMapEnvFrom(prefix="abc", name="configmap", optional=False),
        ],
        env=[
            Env(name="test", value="1"),
            SecretEnv(name="s1", secret_key="s1", secret_name="abc"),
            ResourceEnv(name="r1", resource="abc"),
            ConfigMapEnv(name="c1", config_map_key="c1", config_map_name="abc"),
        ],
    )
```

## Retrying and Timeouts

You can easily set retries and timeouts on templates through the `retry_strategy` and `timeout` members of `TemplateMixin`.

See the example below for a combination of these features, which retries with a backoff up to 10 times or until the
timeout, set at 5 minutes.

```py
from hera.workflows import (
    Container,
    RetryStrategy,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="retry-backoff-til-timeout-",
    entrypoint="retry-backoff-til-timeout",
) as w:
    retry_backoff_til_timeout = Container(
        name="retry-backoff-til-timeout",
        image="python:alpine3.6",
        command=["python", "-c"],
        args=["import random; import sys; exit_code = random.choice([0, 0, 0, 1]); sys.exit(exit_code)"],
        retry_strategy=RetryStrategy(
            limit=10,
            backoff=m.Backoff(
                duration="1",
                factor="2",
                max_duration="1m",
            ),
        ),
        timeout="5m",
    )
```

## Recursion

Individual Steps and Tasks can specify the `Steps` or `DAG` template that it is a part of, allowing recursive Template
Invocators. You must ensure there is a break condition, and you should *NOT* make the first `Step` or `Task` the parent
`Steps` or `DAG` without a condition, otherwise the Argo controller will expand the definition indefinitely until it
crashes.

See the [recursive coinflip](../examples/workflows/upstream/coinflip-recursive.md) example for a recursive `Steps`
template.
