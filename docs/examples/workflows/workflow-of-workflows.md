# Workflow-Of-Workflows






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Resource, Step, Steps, Workflow

    with Workflow(
        generate_name="workflow-of-workflows-1-",
        entrypoint="echo",
    ) as w1:
        Container(name="s", image="docker/whalesay:latest")

    with Workflow(
        generate_name="workflow-of-workflows-2-",
        entrypoint="echo",
    ) as w2:
        Container(name="s", image="docker/whalesay:latest")

    with Workflow(generate_name="workflow-of-workflows-", entrypoint="main") as w:
        w1_res = Resource(
            name="w1-res",
            action="create",
            manifest=w1,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        w2_res = Resource(
            name="w2-res",
            action="create",
            manifest=w2,
            success_condition="status.phase == Succeeded",
            failure_condition="status.phase in (Failed, Error)",
        )

        with Steps(name="main"):
            Step(name="workflow1", template=w1_res)
            Step(name="workflow2", template=w2_res)
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
      - name: w1-res
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName:\
            \ workflow-of-workflows-1-\nspec:\n  entrypoint: echo\n  templates:\n  - container:\n\
            \      image: docker/whalesay:latest\n    name: s\n"
          successCondition: status.phase == Succeeded
      - name: w2-res
        resource:
          action: create
          failureCondition: status.phase in (Failed, Error)
          manifest: "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  generateName:\
            \ workflow-of-workflows-2-\nspec:\n  entrypoint: echo\n  templates:\n  - container:\n\
            \      image: docker/whalesay:latest\n    name: s\n"
          successCondition: status.phase == Succeeded
      - name: main
        steps:
        - - name: workflow1
            template: w1-res
        - - name: workflow2
            template: w2-res
    ```

