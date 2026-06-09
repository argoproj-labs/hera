# Upgrading from Hera v6 to v7

Hera v7 targets Argo Workflows v4 instead of v3.7.
Most code keeps working unchanged because the models and services are regenerated automatically.
Where Argo Workflows v4 dropped a field that Hera's hand-written wrapper still accepts, Hera v7 emits a `DeprecationWarning` and rewrites the call to the v4 equivalent.

The shims will be removed in Hera v8.
Migrate when convenient.

## `CronWorkflow.schedule` -> `schedules`

Argo Workflows v4 removed `CronWorkflowSpec.schedule` in favour of the already-supported `schedules` list (introduced in v3.6).

```py
# v6 / Argo v3 (still works, emits DeprecationWarning)
from hera.workflows import CronWorkflow

with CronWorkflow(
    name="daily-cleanup",
    schedule="0 3 * * *",
) as cw:
    ...
```

```py
# v7 / Argo v4
from hera.workflows import CronWorkflow

with CronWorkflow(
    name="daily-cleanup",
    schedules=["0 3 * * *"],
) as cw:
    ...
```

If both `schedule` and `schedules` are set the legacy value is appended to the list (`schedule="X"` plus `schedules=["Y"]` produces `schedules=["Y", "X"]`), so callers that switched to `schedules` while leaving a stale `schedule` argument in place still get a single, deterministic schedule list on the wire.

## `WorkflowSpec.mutex` / `semaphore` -> `synchronization.mutexes` / `semaphores`

Argo v4 removed the singular `synchronization.mutex` and `synchronization.semaphore` fields, which were already deprecated in v3.6, in favour of `synchronization.mutexes` and `synchronization.semaphores` (both lists).

Hera never exposed `mutex` / `semaphore` on its hand-written `Workflow` or `Template` wrappers, so most users are unaffected.
If you previously reached into `Synchronization` directly through the generated models you will need to move from the singular to the plural form:

```py
# v6 / Argo v3
from hera.workflows import Workflow
from hera.workflows.models import Mutex, Synchronization

with Workflow(
    generate_name="locked-",
    synchronization=Synchronization(mutex=Mutex(name="db")),
) as w:
    ...
```

```py
# v7 / Argo v4
from hera.workflows import Workflow
from hera.workflows.models import Mutex, Synchronization

with Workflow(
    generate_name="locked-",
    synchronization=Synchronization(mutexes=[Mutex(name="db")]),
) as w:
    ...
```

The same applies anywhere `Synchronization` appears in a Hera workflow: template-level synchronization, step-level synchronization, etc.

## `WorkflowSpec.podPriority` -> `priorityClassName`

Argo v4 removed `WorkflowSpec.podPriority` (an integer that was applied to each Pod).
The replacement is `WorkflowSpec.priorityClassName`, which references a Kubernetes `PriorityClass`.

Hera dropped `pod_priority` from its hand-written wrapper surface in v6, so most callers do not need to change anything.
If you were reaching through the generated model directly, switch to a named priority class:

```py
# v6 / Argo v3
from hera.workflows.models import WorkflowSpec

spec = WorkflowSpec(pod_priority=100, ...)
```

```py
# v7 / Argo v4
from hera.workflows.models import WorkflowSpec

spec = WorkflowSpec(priority_class_name="high", ...)
```

## New: `PluginArtifact`

Argo v4 introduces a pluggable artifact driver.
Hera v7 ships a sugar wrapper in `hera.workflows.artifact` matching the existing artifact backend wrappers:

```py
from hera.workflows import PluginArtifact, Workflow, script


@script()
def consumer(message: str) -> None:
    print(message)


with Workflow(generate_name="plugin-artifacts-", entrypoint="consumer") as w:
    consumer(
        arguments={
            "message": PluginArtifact(
                name="payload",
                plugin_name="my-driver",
                key="some/object/path",
                configuration='{"timeout": 10}',
            ),
        },
    )
```

The driver plugin name is exposed as `plugin_name` (not `name`) to avoid shadowing the artifact identifier inherited from `Artifact.name`.

See [Argo's artifact plugin documentation](https://argo-workflows.readthedocs.io/en/latest/plugin-directory/) for the full list of available drivers and how to author your own.
