## Contributing to Hera

**Thank you for considering a contribution to Hera! Your time is the ultimate currency, and the community highly
appreciates your willingness to dedicate some time to Hera for the benefit of everyone!**

Please keep in mind the following guidelines and practices when contributing to Hera:

1. Use `tox -e format` to format the repository code. `tox -e format` maps to a usage of
   [black](https://github.com/psf/black), and the repository adheres to whatever `black` uses as its strict pep8 format.
   No questions asked
1. Use `tox` to lint, run tests, and typecheck on the project
1. Add unit tests for any new code you write
1. Add an example, or extend an existing example, with any new features you may add
1. Increment the version of Hera. Hera adheres to [semantic versioning](https://semver.org/). This increment can be
   performed in the [pyproject.toml](https://github.com/argoproj-labs/hera-workflows/blob/main/pyproject.toml) file. A
   [CHANGELOG](https://github.com/argoproj-labs/hera-workflows/blob/main/CHANGELOG.md) entry is expected along with
   version increases!

### Code of Conduct

Please be mindful of and adhere to the Linux Foundation's
[Code of Conduct](https://lfprojects.org/policies/code-of-conduct) when contributing to Horovod.
