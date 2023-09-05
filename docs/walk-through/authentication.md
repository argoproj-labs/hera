# Authentication

There are multiple ways you can authenticate with Argo Workflows. The way you authenticate generally depends on your
unique organization setup. If you submit workflows through Hera directly you have multiple ways to authenticate with
the Argo server.

Note that the follow examples combine a global config with a workflow submission for illustration purposes. You can
write your own organization thin wrapper, such as `myorg.workflows`, that provides an `__init__.py` to set these
global configurations, along with a `from hera.workflows import *`! Then, if users import everything from your own
module all the configs will apply, and only the workflow definition and submission will be central to a user's
experience. This greatly simplifies the experience, and allows your users to focus on workflow
definition + submission.

## Bearer token

### Workflows service

You can instantiate a `WorkflowsService` if you wish to inject it into a `Workflow` object and use it to submit
workflows!

```python
from hera.workflows import WorkflowsService, Workflow, Container

with Workflow(
    generate_name="test-",
    workflows_service=WorkflowsService(
        host="https://my-argo-server.com",
        token="Bearer abc123",
    ),
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```

### Global configuration

You can set a global configuration for Hera to inject a token into the automatically created `WorkflowsService` object.
The global config token can take multiple types such as a `str`, a function generating a `str`, or a
[TokenGenerator](https://github.com/argoproj-labs/hera/blob/1762bbfcb9b186b62a152b69e04675434a4e76ea/src/hera/auth/__init__.py#L5).

#### Simple `str`

```python
from hera.shared import global_config
from hera.workflows import Workflow, Container

global_config.host = "https://my-argo-server.com"
global_config.token = "abc-123"  # this will be injected to all workflows' services for auth purposes!

with Workflow(
    generate_name="test-",
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```

#### A function that returns a `str` (`Callable[[], Optional[str]]]`)

```python
from typing import Optional

from hera.shared import global_config
from hera.workflows import Workflow, Container


def get_token() -> Optional[str]:
    """Generate an auth token for Hera. This process can do anything and generate a token however you need it to"""
    return "abc-123"


global_config.host = "https://my-argo-server.com"
global_config.token = get_token

with Workflow(
    generate_name="test-",
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```

#### A [TokenGenerator](https://github.com/argoproj-labs/hera/blob/1762bbfcb9b186b62a152b69e04675434a4e76ea/src/hera/auth/__init__.py#L5)

```python
from hera.auth import TokenGenerator
from hera.shared import global_config
from hera.workflows import Workflow, Container


class MyTokenGenerator(TokenGenerator):
    def __call__(self) -> str:
        """Generate an auth token for Hera. This process can do anything and generate a token however you need it to"""
        return "abc-123"


global_config.host = "https://my-argo-server.com"
global_config.token = MyTokenGenerator

with Workflow(
    generate_name="test-",
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```