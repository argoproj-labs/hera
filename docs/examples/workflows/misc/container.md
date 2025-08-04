# Container



This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(generate_name="container-", entrypoint="cowsay") as w:
        Container(name="cowsay", image="argoproj/argosay:v2", command=["cowsay", "foo"])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: container-
    spec:
      entrypoint: cowsay
      templates:
      - name: cowsay
        container:
          image: argoproj/argosay:v2
          command:
          - cowsay
          - foo
    ```

