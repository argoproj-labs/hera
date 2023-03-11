# Suspend





## Hera

```python
from hera.workflows.parameter import Parameter
from hera.workflows.suspend import Suspend
from hera.workflows.workflow import Workflow

with Workflow(generate_name="suspend-") as w:
    Suspend(name="suspend-without-duration")
    Suspend(name="suspend-with-duration", duration=30)
    Suspend(
        name="suspend-with-intermediate-param-enum",
        intermediate_parameters=[Parameter(name="approve", enum=["YES", "NO"], default="NO")],
    )
    Suspend(
        name="suspend-with-intermediate-param",
        intermediate_parameters=[Parameter(name="approve")],
    )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: suspend-
spec:
  templates:
  - name: suspend-without-duration
    suspend: {}
  - name: suspend-with-duration
    suspend:
      duration: '30'
  - inputs:
      parameters:
      - default: 'NO'
        enum:
        - 'YES'
        - 'NO'
        name: approve
    name: suspend-with-intermediate-param-enum
    outputs:
      parameters:
      - name: approve
        valueFrom:
          supplied: {}
    suspend: {}
  - inputs:
      parameters:
      - name: approve
    name: suspend-with-intermediate-param
    outputs:
      parameters:
      - name: approve
        valueFrom:
          supplied: {}
    suspend: {}
```
