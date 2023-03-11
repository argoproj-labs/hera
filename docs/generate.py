import re
import shutil
from pathlib import Path


# This code reads the contents at the path which is a python file,
# extracts the python docstring at the top using a regex and then
# outputs a markdown file with the same name as a python file without the .py extension and
# with a .md extension. The markdown file contains the docstring
# as the initial text block and contains the rest of the python file
# as a python code block. The header of the markdown file is
# generated using the name of the file but converted from snake case
# to sentence case.
def generate_markdown(path: Path, sub_folder: str):
    py_contents = path.read_text()
    match = re.search(r'^"""(.*?)"""', py_contents, re.DOTALL)
    if match:
        docstring = match.group(1)
    else:
        docstring = ""
    # remove the module docstring at the top of the python file using regex
    py_contents = re.sub(r'^(""".*?""")', "", py_contents, 1, re.DOTALL)
    title = path.stem.replace("_", " ").title()
    yaml_contents = Path(str(path).replace(".py", ".yaml").replace("_", "-")).read_text()
    upstream_example = Path(str(path).replace(".py", ".upstream.yaml").replace("_", "-")).exists()
    upstream_link = ""
    if upstream_example:
        upstream_link = f"> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/{path.stem.replace('_', '-') + '.yaml'})."
    contents = f"""# {title}

{upstream_link}

{docstring.strip()}

## Hera

```python
{py_contents.strip()}
```

## YAML

```yaml
{yaml_contents.strip()}
```
"""
    (Path("examples") / sub_folder / path.stem).with_suffix(".md").write_text(contents)


def main():
    # we need to go through each path and generate its markdown
    for sub_folder in ("workflows", "workflows/upstream"):
        folder = Path("examples") / sub_folder
        shutil.rmtree(folder, ignore_errors=True)
        (folder).mkdir(parents=True, exist_ok=True)
        for path in Path(f"../examples/{sub_folder}").glob("*.py"):
            if path.stem != "__init__":
                generate_markdown(path, sub_folder)


if __name__ == "__main__":
    main()
