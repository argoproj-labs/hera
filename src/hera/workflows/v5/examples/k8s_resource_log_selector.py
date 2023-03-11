from hera.workflows.v5.resource import Resource
from hera.workflows.v5.workflow import Workflow

tf_jobtmpl = Resource(
    name="tf-jobtmpl",
    action="create",
    success_condition="status.replicaStatuses.Worker.succeeded = 2",
    failure_condition="status.replicaStatuses.Worker.failed > 0",
    manifest="""apiVersion: kubeflow.org/v1
kind: TFJob
metadata:
  name: tfjob-examples
spec:
  tfReplicaSpecs:
     Worker:
       replicas: 2
       restartPolicy: Never
       template:
         metadata:
           # We add this label to the pods created by TFJob custom resource to inform Argo Workflows
           # that we want to include the logs from the created pods. Once the pods are created with this
           # label, you can then use `argo logs -c tensorflow` to the logs from this particular container.
           # Note that `workflow.name` is a supported global variable provided by Argo Workflows.
           #
           # The Kubeflow training controller will take this CRD and automatically created worker pods with
           # labels, such as `job-role` and `replica-index`. If you'd like to query logs for pods with
           # specific labels, you can specify the label selector explicitly via `argo logs -l <logs-label-selector>`.
           # For example, you can use `argo logs -c tensorflow -l replica-index=0` to see the first worker pod's logs.
           labels:
             workflows.argoproj.io/workflow: {{workflow.name}}
         spec:
           containers:
             - name: tensorflow
               image: "Placeholder for TensorFlow distributed training image\"""",
)

w = Workflow(generate_name="k8s-jobs-log-selector-", entrypoint="tf-jobtmpl", templates=[tf_jobtmpl])
