import re
from pathlib import Path

# This code reads the contents at the path which is a python file,
# extracts the python docstring at the top using a regex and then
# outputs a markdown file with the same name as a python file without the .py extension and
# with a .md extension. The markdown file contains the docstring
# as the initial text block and contains the rest of the python file
# as a python code block. The header of the markdown file is
# generated using the name of the file but converted from snake case
# to sentence case.
def generate_markdown(path: Path):
    contents = path.read_text()
    match = re.search(r'^"""(.*?)"""', contents, re.DOTALL)
    if match:
        docstring = match.group(1)
    else:
        docstring = ""
    # remove the module docstring at the top of the python file using regex
    contents = re.sub(r'^(""".*?""")', "", contents, 1, re.DOTALL)
    title = path.stem.replace("_", " ").title()
    contents = f"""# {title}

{docstring.strip()}

```python
{contents.strip()}
```
"""
    (Path("examples")/ path.stem).with_suffix(".md").write_text(contents)


def main():
    # we need to go through each path and generate its markdown
    for path in Path("../examples").glob("*.py"):
        generate_markdown(path)

if __name__ == "__main__":
    main()
