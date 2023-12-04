# K8S Resource Log Selector

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-resource-log-selector.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resource, Workflow

    with Workflow(generate_name="k8s-jobs-log-selector-", entrypoint="tf-jobtmpl") as w:
        tf_jobtmpl = Resource(
            name="tf-jobtmpl",
            action="create",
            success_condition="status.replicaStatuses.Worker.succeeded = 2",
            failure_condition="status.replicaStatuses.Worker.failed > 0",
            manifest=r"""apiVersion: kubeflow.org/v1
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
                   image: "Placeholder for TensorFlow distributed training image"
    """,
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: k8s-jobs-log-selector-
    spec:
      entrypoint: tf-jobtmpl
      templates:
      - name: tf-jobtmpl
        resource:
          action: create
          failureCondition: status.replicaStatuses.Worker.failed > 0
          manifest: "apiVersion: kubeflow.org/v1\nkind: TFJob\nmetadata:\n  name: tfjob-examples\n\
            spec:\n  tfReplicaSpecs:\n     Worker:\n       replicas: 2\n       restartPolicy:\
            \ Never\n       template:\n         metadata:\n           # We add this label\
            \ to the pods created by TFJob custom resource to inform Argo Workflows\n\
            \           # that we want to include the logs from the created pods. Once\
            \ the pods are created with this\n           # label, you can then use `argo\
            \ logs -c tensorflow` to the logs from this particular container.\n      \
            \     # Note that `workflow.name` is a supported global variable provided\
            \ by Argo Workflows.\n           #\n           # The Kubeflow training controller\
            \ will take this CRD and automatically created worker pods with\n        \
            \   # labels, such as `job-role` and `replica-index`. If you'd like to query\
            \ logs for pods with\n           # specific labels, you can specify the label\
            \ selector explicitly via `argo logs -l <logs-label-selector>`.\n        \
            \   # For example, you can use `argo logs -c tensorflow -l replica-index=0`\
            \ to see the first worker pod's logs.\n           labels:\n             workflows.argoproj.io/workflow:\
            \ {{workflow.name}}\n         spec:\n           containers:\n            \
            \ - name: tensorflow\n               image: \"Placeholder for TensorFlow distributed\
            \ training image\"\n"
          successCondition: status.replicaStatuses.Worker.succeeded = 2
    ```

