---
name: "\U0001F41B Bug report"
about: Help us fix something!
title: ''
labels: 'type:bug'
assignees: ''

---

<h2>Pre-bug-report checklist</h2>

**1. This bug can be reproduced using YAML**
- [ ] Yes [👉 Please report a bug to the Argo Workflows GitHub 👈](https://github.com/argoproj/argo-workflows/issues/new/choose)
- [ ] No

**2. This bug occurs when...**
- [ ] running Hera code without submitting to Argo (e.g. when exporting to YAML)
- [ ] running Hera code and submitting to Argo

<h2>Bug report</h2>

**Describe the bug**
_A clear and concise description of what the bug is:_

_Error log if applicable_:
```
error: something broke!
```

**To Reproduce**
Full Hera code to reproduce the bug:
```py
from hera.workflows import Workflow

with Workflow(name="my-workflow") as w:
    # Add your code here
```

**Expected behavior**
_A clear and concise description of what you expected to happen:_


**Environment**
- Hera Version: 5.X.X
- Python Version: 3.X.X
- Version of Argo: 3.X.X

**Additional context**
Add any other context about the problem here.
