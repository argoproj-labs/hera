# Authentication

The way you authenticate generally depends on your unique organization setup. You could either directly authenticate against the Argo server, or you handle authentication directly through the reverse proxy, or even both. 

If you submit workflows through Hera
directly you have multiple ways to authenticate with the Argo server.

Note that the follow examples combine a global config with a workflow submission for illustration purposes. You can
write a thin wrapper for your own organization, such as `myorg.workflows`, that provides an `__init__.py` to set these
global configurations, along with a `from hera.workflows import *`! Then, if users import everything from your own
module all the configs will apply, and only the workflow definition and submission will be central to a user's
experience. This greatly simplifies the experience, and allows your users to focus on workflow definition + submission.

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

#### A [TokenGenerator](https://github.com/argoproj-labs/hera/blob/1762bbfcb9b186b62a152b69e04675434a4e76ea/src/hera/auth/__init__.py#L22)

##### Generating a plain string token via a `TokenGenerator`

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

##### Generating a K8s token via `TokenGenerator`

```python
import base64
import errno
import os
from typing import Optional

# note: you need to install the `kubernetes` dependency as Hera does not provide this
from kubernetes import client, config

from hera.auth import TokenGenerator
from hera.shared import global_config
from hera.workflows import Workflow, Container


class K8sTokenGenerator(TokenGenerator):
    def __init__(self, service_account: str, namespace: str = "default", config_file: Optional[str] = None) -> None:
        self.service_account = service_account
        self.namespace = namespace
        self.config_file = config_file

    def __call__(self) -> str:
        if self.config_file is not None and not os.path.isfile(self.config_file):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.config_file)

        config.load_kube_config(config_file=self.config_file)
        v1 = client.CoreV1Api()
        secret_name = v1.read_namespaced_service_account(self.service_account, self.namespace).secrets[0].name
        sec = v1.read_namespaced_secret(secret_name, self.namespace).data
        return base64.b64decode(sec["token"]).decode()


global_config.host = "https://my-argo-server.com"
global_config.token = K8sTokenGenerator("my-service-account")

# the workflow automatically creates a workflow service, which uses the global config
# host and token generator for authentication
with Workflow(
    generate_name="test-",
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```

## Client Certificates

There are cases where your org might have client certificate authentication enabled which means that you'd have to present a client cert + key everytime you wish to access a UI or API. 
In those cases you could either pass the certs on the global config or directly into the `WorkflowService`

### Workflow Service

```python
from hera.workflows import WorkflowsService, Workflow, Container

with Workflow(
    generate_name="test-",
    workflows_service=WorkflowsService(
        host="https://my-argo-server.com",
        token="Bearer abc123",
    ),
    client_certs=("/path-to-client-cert","/path-to-client-key")
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```

## Global configuration

You can set a global configuration for Hera to inject the client certificates into the automatically created `WorkflowsService` object.
The global config token can take multiple types such as a `(str, str)` or `(Path, Path)` tuple or a function generating a `(str, str) or (Path, Path)`.

#### Simple `(str,str)`

```python
from hera.shared import global_config
from hera.workflows import Workflow, Container

global_config.host = "https://my-argo-server.com"
global_config.token = "abc-123"  # this will be injected to all workflows' services for auth purposes!
global_config.client_certs = ("/path-to-client-cert","/path-to-client-key")
with Workflow(
    generate_name="test-",
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```

#### A function that returns a `(str, str) or (Path, Path)` (`Callable[[], Union[Optional[Tuple[Path, Path]], Optional[Tuple[str, str]]]]`)

```python
from typing import Optional,Tuple
from pathlib import Path
from hera.shared import global_config
from hera.workflows import Workflow, Container


def get_certs() -> Optional[Tuple[str,str]]:
    """Generate or grab client certs for Hera. 
    This process can do anything and generate a token however you need it to"""
    return ("/path-to-client-cert","/path-to-client-key")

def get_cert_paths() -> Optional[Tuple[Path, Path]]:
    return (Path("/path-to-client-cert"), Path("/path-to-client-key"))


global_config.host = "https://my-argo-server.com"
global_config.token = get_certs # or get_cert_paths

with Workflow(
    generate_name="test-",
    entrypoint="c",
) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])

w.create()
```