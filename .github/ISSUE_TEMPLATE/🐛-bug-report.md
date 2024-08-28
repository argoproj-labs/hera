---
name: "\U0001F41B Bug report"
about: Help us fix something!
title: ''
labels: 'type:bug'
assignees: ''

---

<h2>Pre-bug-report checklist</h2>

**1. This bug can be reproduced using pure Argo YAML**
- [ ] Yes [👉 Please report a bug to the Argo Workflows GitHub 👈](https://github.com/argoproj/argo-workflows/issues/new/choose)
- [ ] No

_If yes, it is more likely to be an Argo bug unrelated to Hera. Please double check before submitting an issue to Hera._

**2. I have searched for [existing issues](https://github.com/argoproj-labs/hera/issues)**
- [ ] Yes

**3. This bug occurs in Hera when...**
- [ ] exporting to YAML
- [ ] submitting to Argo
- [ ] running on Argo with the Hera runner
- [ ] other: 

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
- Argo Version: 3.X.X

**Additional context**
Add any other context about the problem here.
