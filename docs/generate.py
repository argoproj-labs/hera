"""Module that holds the functionality that generates Hera's documentation."""

import os
import re
import shutil
import textwrap
from pathlib import Path


def generate_markdown(path: Path, sub_folder: str) -> str:
    """Generates the Markdown version of the documentation of the file located at the given path, into the given sub_folder.

    This code reads the contents at the path which is a python file,
    extracts the python docstring at the top using a regex and then
    outputs a markdown file with the same name as a python file without the .py extension and
    with a .md extension. The markdown file contains the docstring
    as the initial text block and contains the rest of the python file
    as a python code block. The header of the markdown file is
    generated using the name of the file but converted from snake case
    to sentence case.
    """
    py_contents = path.read_text()
    link = "https://github.com/argoproj/argo-workflows/blob/main/examples/{link}".format(
        link=path.stem.replace("__", "/").replace("_", "-") + ".yaml"
    )
    match = re.search(r'^"""(.*?)"""', py_contents, re.DOTALL)
    if match:
        docstring = match.group(1)
    else:
        docstring = ""
    # remove the module docstring at the top of the python file using regex
    py_contents = re.sub(r'^(""".*?""")', "", py_contents, 1, re.DOTALL)
    title = path.stem.replace("_", " ").title()
    yaml_filename = path.stem.replace("_", "-")
    yaml_contents = (path.parent / (yaml_filename + ".yaml")).read_text()
    upstream_example = (path.parent / (yaml_filename + ".upstream.yaml")).exists()
    upstream_link = ""
    if upstream_example:
        upstream_link = (
            "## Note\n\n"
            "This example is a replication of an Argo Workflow example in Hera.\n"
            f"The upstream example can be [found here]({link})."
        )
    contents = f"""# {title}

{upstream_link}

{docstring.strip()}


=== "Hera"

    ```python linenums="1"
{textwrap.indent(py_contents.strip(), "    ")}
    ```

=== "YAML"

    ```yaml linenums="1"
{textwrap.indent(yaml_contents.strip(), "    ")}
    ```

"""
    (Path(sub_folder) / path.stem).with_suffix(".md").write_text(contents)


def _main():
    """Go through example python files and generate markdown for the readthedocs website."""
    examples_workflows = "examples/workflows"
    for example_sub_folder in ["workflows"] + [
        f"workflows/{name}"
        for name in os.listdir(f"../{examples_workflows}")
        if os.path.isdir(os.path.join(f"../{examples_workflows}", name)) and name != "__pycache__"
    ]:
        # Use hyphens for website URL paths
        docs_example_sub_folder = f'examples/{example_sub_folder.replace("_", "-")}'
        shutil.rmtree(docs_example_sub_folder, ignore_errors=True)
        Path(docs_example_sub_folder).mkdir(parents=True, exist_ok=True)
        for path in Path(f"../examples/{example_sub_folder}").glob("*.py"):
            if path.stem != "__init__":
                generate_markdown(path, docs_example_sub_folder)


if __name__ == "__main__":
    _main()
