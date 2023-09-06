# Workflow Of Workflows






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Resource, Step, Steps, Workflow

    with Workflow(
        generate_name="sub-workflow-1-",
        entrypoint="echo",
    ) as sub_workflow_1:
        Container(
            name="echo",
            image="docker/whalesay:latest",
            command=["whalesay"],
            args=["I'm workflow 1"],
        )

    with Workflow(
        generate_name="sub-workflow-2-",
        entrypoint="echo",
    ) as sub_workflow_2:
        Container(
            name="echo",
            image="docker/whalesay:latest",
            command=["whalesay"],
            args=["I'm workflow 2"],
        )

    with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
        w1_resource = Resource(
            name="w1-resource",
            action="create",
            manifest=sub_workflow_1,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        w2_resource = Resource(
            name="w2-resource",
            action="create",
            manifest=sub_workflow_2,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        with Steps(name="main"):
            Step(name="sub-workflow-1", template=w1_resource)
            Step(name="sub-workflow-2", template=w2_resource)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-of-workflows-
    spec:
      entrypoint: main
      templates:
      - name: w1-resource
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName:\
            \ sub-workflow-1-\nspec:\n  entrypoint: echo\n  templates:\n  - container:\n\
            \      args:\n      - I'm workflow 1\n      command:\n      - whalesay\n \
            \     image: docker/whalesay:latest\n    name: echo\n"
          successCondition: status.phase == Succeeded
      - name: w2-resource
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName:\
            \ sub-workflow-2-\nspec:\n  entrypoint: echo\n  templates:\n  - container:\n\
            \      args:\n      - I'm workflow 2\n      command:\n      - whalesay\n \
            \     image: docker/whalesay:latest\n    name: echo\n"
          successCondition: status.phase == Succeeded
      - name: main
        steps:
        - - name: sub-workflow-1
            template: w1-resource
        - - name: sub-workflow-2
            template: w2-resource
    ```

