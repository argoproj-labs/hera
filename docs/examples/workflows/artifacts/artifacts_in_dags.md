# Artifacts In Dags



This example shows how to use artifacts as inputs and outputs of DAGs.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, Container, Workflow

    with Workflow(
        generate_name="artifacts-in-dags-",
        entrypoint="runner-dag",
    ) as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["sleep 1; echo hello world | tee /tmp/hello_world.txt"],
            outputs=[Artifact(name="hello-art", path="/tmp/hello_world.txt")],
        )
        print_message_from_file = Container(
            name="print-message-from-file",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[Artifact(name="message", path="/tmp/message")],
        )

        # First DAG generates an artifact from a task, and "lifts" it out as an output of the DAG template itself
        with DAG(
            name="generate-artifact-dag",
            outputs=[Artifact(name="hello-file", from_="{{tasks.hello-world-to-file.outputs.artifacts.hello-art}}")],
        ) as d1:
            hello_world_to_file()

        # Second DAG takes an artifact input, and the task references it using `get_artifact`
        with DAG(name="consume-artifact-dag", inputs=[Artifact(name="hello-file-input")]) as d2:
            print_message_from_file(
                arguments=d2.get_artifact("hello-file-input").with_name("message"),
            )

        # Third DAG orchestrates the first two, by creating tasks by "calling" the objects
        with DAG(name="runner-dag"):
            generator_dag = d1()
            consumer_dag = d2(arguments=generator_dag.get_artifact("hello-file").with_name("hello-file-input"))

            generator_dag >> consumer_dag
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifacts-in-dags-
    spec:
      entrypoint: runner-dag
      templates:
      - container:
          args:
          - sleep 1; echo hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: busybox
        name: hello-world-to-file
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
      - container:
          args:
          - cat /tmp/message
          command:
          - sh
          - -c
          image: alpine:latest
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
        name: print-message-from-file
      - dag:
          tasks:
          - name: hello-world-to-file
            template: hello-world-to-file
        name: generate-artifact-dag
        outputs:
          artifacts:
          - from: '{{tasks.hello-world-to-file.outputs.artifacts.hello-art}}'
            name: hello-file
      - dag:
          tasks:
          - arguments:
              artifacts:
              - from: '{{inputs.artifacts.hello-file-input}}'
                name: message
            name: print-message-from-file
            template: print-message-from-file
        inputs:
          artifacts:
          - name: hello-file-input
        name: consume-artifact-dag
      - dag:
          tasks:
          - name: generate-artifact-dag
            template: generate-artifact-dag
          - arguments:
              artifacts:
              - from: '{{tasks.generate-artifact-dag.outputs.artifacts.hello-file}}'
                name: hello-file-input
            depends: generate-artifact-dag
            name: consume-artifact-dag
            template: consume-artifact-dag
        name: runner-dag
    ```

