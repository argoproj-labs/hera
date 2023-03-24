# Workflow Template  Workflow Template Ref

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-template/workflow-template-ref.yaml).



## Hera

```python
from hera.workflows import Workflow
from hera.workflows.models import WorkflowTemplateRef

wt_ref = WorkflowTemplateRef(name="workflow-template-submittable")

w = Workflow(
    generate_name="workflow-template-hello-world-",
    workflow_template_ref=wt_ref,
)
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: workflow-template-hello-world-
spec:
  workflowTemplateRef:
    name: workflow-template-submittable
```
