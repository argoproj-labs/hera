# Title And Description With Markdown

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/title-and-description-with-markdown.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/title": "**Test Title**",
            "workflows.argoproj.io/description": "`This is a simple hello world example.`\nThis is an embedded link to the docs: https://argo-workflows.readthedocs.io/en/latest/title-and-description/\n",
        },
        generate_name="title-and-description-with-markdown-",
        labels={"workflows.argoproj.io/archive-strategy": "false"},
        entrypoint="hello-world",
    ) as w:
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: title-and-description-with-markdown-
      annotations:
        workflows.argoproj.io/description: |
          `This is a simple hello world example.`
          This is an embedded link to the docs: https://argo-workflows.readthedocs.io/en/latest/title-and-description/
        workflows.argoproj.io/title: '**Test Title**'
      labels:
        workflows.argoproj.io/archive-strategy: 'false'
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
    ```

