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
