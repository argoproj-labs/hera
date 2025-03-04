# Template On Exit

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/template-on-exit.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Workflow
    from hera.workflows.models import LifecycleHook

    with Workflow(generate_name="container-on-exit-", entrypoint="step-template") as w:
        exit_container = Container(
            name="exitContainer",
            image="busybox",
            command=["echo"],
            args=["goodbye world"],
        )
        hello_world = Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
        )
        with Steps(name="step-template"):
            hello_world(name="stepA", hooks={"exit": LifecycleHook(template=exit_container.name)})
            hello_world(name="stepB", hooks={"exit": LifecycleHook(template=exit_container.name)})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: container-on-exit-
    spec:
      entrypoint: step-template
      templates:
      - name: exitContainer
        container:
          image: busybox
          args:
          - goodbye world
          command:
          - echo
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      - name: step-template
        steps:
        - - hooks:
              exit:
                template: exitContainer
            name: stepA
            template: hello-world
        - - hooks:
              exit:
                template: exitContainer
            name: stepB
            template: hello-world
    ```

