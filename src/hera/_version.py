from importlib import metadata

name = "hera"  # project-name
# Used to automatically set version number from github actions
# as well as not break when being tested locally
try:
    version = metadata.version(name)
except metadata.PackageNotFoundError:  # pragma: no cover
    version = "0.0.0-dev"
