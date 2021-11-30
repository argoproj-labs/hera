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