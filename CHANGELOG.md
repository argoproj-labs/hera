# CHANGELOG

This file follows [semantic versioning 2.0.0](https://semver.org/). Given a version number MAJOR.MINOR.PATCH, increment
the:

- **MAJOR** version when you make incompatible API changes,
- **MINOR** version when you add functionality in a backwards compatible manner, and
- **PATCH** version when you make backwards compatible bug fixes.

As a heuristic:

- if you fix a bug, increment the PATCH
- if you add a feature (add keyword arguments with default values, add a new object, a new mechanism for parameter setup
  that is backwards compatible, etc.), increment the MINOR version
- if you introduce a breaking change (removing arguments, removing objects, restructuring code such that it affects
  imports, etc.), increment the MAJOR version

The general format is:

```

# VERSION - DATE (dd/mm/yyyy)
### Added
- A to B
### Changed
- B to C
### Removed
- C from D

```

# 3.7.0 - DATE (26/08/2022)

### Added

- support for Git artifact authentication credentials
- tolerations can now be set via workflow
- version via `hera.__version__`

### Changed

- float type handling for `max_cpu` and `min_cpu` properties in `Resources` class
- kwarg value setting as a parameter

# 3.6.4 - DATE (11/08/2022)

### Removed

- Remove python <3.11 constraint and unpin transitive dependencies

# 3.6.3 - DATE (01/08/2022)

### Changed

- `pytz` version from `^2021.3` to `>=2021.3`

### Added

- workflow template parameters
- privileged option to the security context

# 3.6.2 - DATE (29/07/2022)

### Changed

- `Config.host` and `Config.verify_ssl` are now public; `WorkflowService.get_workflow_link` now references `Config.host`
  to properly pull the host when using `set_global_host`.

# 3.6.1 - DATE (17/07/2022)

### Removed

- `get_input_spec` from `InputArtifact` so that it relies on the inherited one that does not add the `from` field that
  is not allowed in the Argo submission for input artifacts

# 3.6.0 - DATE (10/07/2022)

### Added

- support for `subPath` in volume mounts
- context management to workflow types. This supports the `with` clause and adds all tasks to a workflow automatically
- task exit hook
- HTTP artifact
- global workflow parameters
- input parameter caching through memoization
- bucket field to GCS/S3 artifact, which was missing

### Removed

- assertion that `input_from` cannot be used with artifacts, which supports artifact input on fanned out tasks now

# 3.5.0 - DATE (14/06/2022)

### Added

- support for multiple inputs from a fanned out task via `MultiInput`

### Changed

- `set_global_token` to take in a union of a string token or a callable

# 3.4.0 - DATE (12/06/2022)

### Added

- node selectors on all workflow types
- memoization
- global parameter access on tasks
- input/output parameters in addition to artifacts
- affinity, anti-affinity, node affinity
- client host/token global injection

# 3.3.2 - DATE (30/05/2022)

### Fixed

- parallelism specification on spec templates

# 3.3.1 - DATE (26/05/2022)

### Fixed

- Fix Task raise error with input_from without func

# 3.3.0 - DATE (23/05/2022)

### Added

- `AnySucceeded`/`AllFailed` support on tasks
- `OnExit` condition on workflows with tasks conditioned on `WorkflowStatus`
- plain string support when using `InputFrom`
- `argo-workflows==6.3.5` dependency

### Removed

- JSON import from tasks that do not need it
- references to `IoArgoprojWorkflowV1alpha1WorkflowTemplateSpec` and instead
  use `IoArgoprojWorkflowV1alpha1WorkflowSpec`

# 3.2.0 - DATE (15/05/2022)

### Added

- cluster scope in template reference
- host alias support
- volume claim garbage collection setting on workflows
- git artifact

### Changed

- structure of the environment variables. Now contributors can implement the generic `Variable` rather than augment or
  duplicate `VariableAsEnv`

# 3.1.0 - DATE (28/04/2022)

### Added

- retry policy support

### Changed

- implementation of the cron workflow update command so that it includes the version and the assigned cron workflow UUID
  during the update operation

# 3.0.0 - DATE (04/10/2022)

### Added

- update method to CronWorkflowService
- ability to track workflow status
- shared implementation of `add_head`, `add_tail`, `add_task`, `add_tasks`
- task workflow template reference

### Removed

- UUID suffixes

# 2.9.1 - DATE (04/11/2022)

### Fixed

- prevent json.loads error when task has input from other tasks(with the json dumped string contains single quote)

# 2.9.0 - DATE (04/08/2022)

### Added

- Add support for TTLStrategy([link](https://argoproj.github.io/argo-workflows/fields/#ttlstrategy))

# 2.8.1 - DATE (04/08/2022)

### Fixed

- fix wrong dependencies when calling on_success(), on_failure(), on_error() functions of Sask

# 2.8.0 - DATE (04/07/2022)

### Added

- add support for exposing field reference via env vars in Tasks

# 2.7.0 - DATE (04/06/2022)

### Added

- add support for specifying annotations on Workflows, CronWorkflows and Tasks

# 2.6.0 - DATE (29/03/2022)

### Added

- retry limit

# 2.5.0 - DATE (29/03/2022)

### Added

- image pull secrets option on workflows
- ability to set a task dependency and execution based on the success, failure, or error of another task (similar
  to `when`)
- support for `env_from` option

# 2.4.0 - DATE (22/03/2022)

### Added

- Set image_pull_policy on a Task level
- WorkflowTemplate Service and WorkflowTemplate implementation
- Option to create a Workflow with a WorkflowTemplate

# 2.3.0 - DATE (29/03/2022)

### Added

- ability to set the `access_modes` for dynamically provisioned volumes
- security context on cron workflows
- image pull secrets specification on workflows and cron workflows

# 2.2.1 - DATE (05/03/2022)

### Fixed

- inconsistency between `create` and `submit` between Hera and Argo. Now users are provided with a `create` command and
  will receive a `DeprecationWarning` when the `submit` is invoked

# 2.2.0 - DATE (17/02/2022)

### Added

- Add support for sharing the IP of one Task to another Task, via env variables
- support for setting args instead of command

# 2.1.1 - DATE (16/02/2022)

### Changed

- Added `volume_mounts` definition back to script template in `Task.get_script_def`.

# 2.1.0 - DATE (15/02/2022)

### Added

- Added `TaskSecurityContext` to allow setting security settings to the task container.
- Added `WorkflowSecurityContext` to allow setting security settings to all of the containers in the workflow.

# 2.0.0 - DATE (08/02/2022)

### Added

- support for custom resources on `Resource` definitions

# 2.0.0rc1 - DATE (08/02/2022)

### Added

- support for multiple volumes (volumes, config maps, secrets, existing volumes)

# 1.8.0rc7 - DATE (08/02/2022)

### Added

- add support for bucket resource inputs with key only

# 1.8.0rc6 - DATE (08/02/2022)

### Changed

- wait time for Test PyPi in CICD from 30 to 60 seconds

# 1.8.0rc5 - DATE (08/02/2022)

### Added

- add image pull policy on tasks

# 1.8.0rc4 - DATE (08/02/2022)

### Added

- add ability to mount config maps as volume in a task

# 1.8.0rc3 - DATE (08/02/2022)

### Added

- a `sleep` step to the new Hera version installation from Test PyPI to wait for PyPI indexing

# 1.8.0rc2 - DATE (08/02/2022)

### Changed

- GitHub test index installation for CICD

# 1.8.0rc1 - DATE (08/02/2022)

### Changed

- the underlying SDK from argo-workflows v5 to argo-workflows v6.3rc2

# 1.7.0 - DATE (30/01/2022)

### Added

- don't require func to be specified when creating a task, running the task as only a container with commands

# 1.6.2 - DATE (30/01/2022)

### Changed

- fix where a subclass of a Task could not have the parent type as dependency

# 1.6.1 - DATE (26/01/2022)

### Changed

- the type for the `value` field of `EnvSpec` from `Optional[Union[BaseModel, Any]]` to only `Optional[Any]` as
  dictionary values were not serialized/set properly as a consequence of Pydantic validation

# 1.6.0 - DATE (26/01/2022)

### Added

- add default name/namespace handling to CronWorkflow create/suspend/resume methods

# 1.5.1 - DATE (25/01/2022)

### Changed

- `EnvSpec` to return the `value` if `value` is of type string

# 1.5.0 - DATE (24/01/2022)

### Added

- add support for exposing config map keys via env vars in Tasks

# 1.4.0 - DATE (23/01/2022)

### Added

- add support for attaching a secret volume to Workflows and CronWorkflows

# 1.3.0 - DATE (20/01/2022)

### Added

- add support for specifying labels on Workflows, CronWorkflows and Tasks

# 1.2.0 - DATE (18/01/2022)

### Added

- add support for the timezone attribute of CronWorkflow and validate the specified timezone
- introduce `pytz` dependency for timezone validation

# 1.1.0 - DATE (17/01/2022)

### Added

- The `daemon` keyword to the Task. `deamon` will allow a workflow to proceed to the next task, so long as the container
  reaches readiness.

# 1.0.2 - DATE (17/01/2022)

### Changed

- Make value in Tolerations optional, as per Kubernetes requirements

# 1.0.1 - DATE (11/01/2022)

### Changed

- `setup.py` packages field to include hera exclusively post-removal of the underlying `v1` directory. With the removal
  of the underlying versioned subpackage (`v1`) in 1.0.0 the `setup.py` file no longer installed the necessary modules
  as the wheel only included references for whatever subpackages were in `hera.*` but not `hera`
  itself (as a module)

# 1.0.0 - DATE (10/01/2022)

### Removed

- `v1` submodule of Hera to avoid internal versioning and external/package versioning

### Changed

- location of all files from `v1` up one folder to `hera`. Now everything will take the import form
  of `from hera.module import Object` rather than `from hera.v1.module import Object`
- interface of services to take a full host rather than a single domain and put in effort to compute the final host.
  This will offer more freedom to users to select their own host scheme, for example. A flag for SSL verification was
  also introduced
- all volume types (existing, empty dir, and regular volume) are now packaged in the volumes module rather than
  separated

# 0.4.2 - DATE (10/01/2022)

### Added

- an `overwrite_maxs` to `Resource` to allow users to set whether max resources should be set to min values when they
  are not specified

# 0.4.1 - DATE (09/01/2022)

### Changed

- underlying SDK of Hera, which moved from `argo-workflows` to the Argo Workflows repository (unpublished on PyPi)
  Python SDK. This was originally released in https://github.com/argoproj-labs/hera-workflows/pull/38 but the
  publication process to PyPi failed. A fix was attempted in https://github.com/argoproj-labs/hera-workflows/pull/43
  but that published a broken version because the `dependency_links` of `setup.py` did not actually install the
  necessary dependency. As a consequence, the release was quickly deleted from PyPi because it was broken. The best
  course of action was to wait for the official release of the new SDK under `argo-workflows==6.0.0`, in collaboration
  with the maintainers of https://github.com/argoproj/argo-workflows

# 0.4.0 - DATE (15/12/2021)

### Added

- input/output artifact specifications

# 0.3.1 - DATE (04/12/2021)

### Changed

- fix returned value of validator method in EnvSpec class

# 0.3.0 - DATE (30/11/2021)

### Added

- added support to `when` workflows API.

# 0.2.0 - DATE (30/11/2021)

### Added

- ability to specify a service account name to run the workflow as. This is currently set on the workflow level only,
  which makes all the pods of tasks in a workflow use the same service account.

# 0.1.1 - DATE (17/11/2021)

### Changed

- the publication step of Hera. The `python` command will now build an `sdist` and a `wheel` for the package
- relocked the project to include `wheel` as a development dependency

# 0.1.0 - DATE (03/11/2021)

### Added

- added initial support for cron workflows

# 0.0.0 - DATE (28/10/2021)

### Added

- initial release of Hera
