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

# 1.1.0 - DATE (17/01/2022)

### Added
  - The `daemon` keyword to the Task. `deamon` will allow a workflow to proceed to the next task,
    so long as the container reaches readiness.
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
