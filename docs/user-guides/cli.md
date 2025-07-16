# Hera CLI

!!! warning
    The Hera CLI is an experimental work-in-progress, and may change at any time!

The Hera CLI offers some limited capabilities for converting to and from YAML files. Install it using:

```
pip install hera[cli]
```

## Converting Python to YAML

```
hera generate yaml [--to TO] [--recursive] [-i INCLUDE] [-e EXCLUDE] FROM [-h]
```

Hera will detect any `Workflow` objects defined at the top-level of the specified file or files (within a specified
directory), and output to stdout or the specified output file. Read more by using the help command
`hera generate yaml -h`.

## Converting YAML to Python

!!! warning
    This feature is *heavily* experimental and subject to change!

```
hera generate python [--to TO] [--recursive] [-i INCLUDE] [-e EXCLUDE] FROM [-h]
```

Hera can generate Python code from a given Workflow definition in YAML, and works for over 90% of the upstream example
collection (i.e. Hera can generate Python code, which in turn generates equivalent YAML for these examples).

This feature is intended to be a springboard for converting a collection of YAML Workflows into Python, and should not
be considered the optimal way to write Workflows. The command will overwrite anything that exists at the given file location,
so is not able to merge user code and generated code.
