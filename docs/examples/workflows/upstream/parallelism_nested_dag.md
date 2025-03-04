# Parallelism Nested Dag

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/parallelism-nested-dag.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    one_job = Container(
        name="one-job",
        inputs=Parameter(name="msg"),
        image="alpine",
        command=["/bin/sh", "-c"],
        args=["echo {{inputs.parameters.msg}}; sleep 10"],
    )

    with Workflow(generate_name="parallelism-nested-dag-", entrypoint="A") as w:
        with DAG(name="B", inputs=Parameter(name="msg")) as B:
            c1 = one_job(name="c1", arguments={"msg": "{{inputs.parameters.msg}} c1"})
            c2 = one_job(name="c2", arguments={"msg": "{{inputs.parameters.msg}} c2"})
            c3 = one_job(name="c3", arguments={"msg": "{{inputs.parameters.msg}} c3"})
            c1 >> [c2, c3]

        with DAG(name="A", parallelism=2) as A:
            b1 = B(name="b1", arguments={"msg": "1"})
            b2 = B(name="b2", arguments={"msg": "2"})
            b3 = B(name="b3", arguments={"msg": "3"})
            b4 = B(name="b4", arguments={"msg": "4"})
            b5 = B(name="b5", arguments={"msg": "5"})
            b1 >> [b2, b3, b4] >> b5
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parallelism-nested-dag-
    spec:
      entrypoint: A
      templates:
      - name: B
        dag:
          tasks:
          - name: c1
            template: one-job
            arguments:
              parameters:
              - name: msg
                value: '{{inputs.parameters.msg}} c1'
          - name: c2
            depends: c1
            template: one-job
            arguments:
              parameters:
              - name: msg
                value: '{{inputs.parameters.msg}} c2'
          - name: c3
            depends: c1
            template: one-job
            arguments:
              parameters:
              - name: msg
                value: '{{inputs.parameters.msg}} c3'
        inputs:
          parameters:
          - name: msg
      - name: one-job
        container:
          image: alpine
          args:
          - echo {{inputs.parameters.msg}}; sleep 10
          command:
          - /bin/sh
          - -c
        inputs:
          parameters:
          - name: msg
      - name: A
        parallelism: 2
        dag:
          tasks:
          - name: b1
            template: B
            arguments:
              parameters:
              - name: msg
                value: '1'
          - name: b2
            depends: b1
            template: B
            arguments:
              parameters:
              - name: msg
                value: '2'
          - name: b3
            depends: b1
            template: B
            arguments:
              parameters:
              - name: msg
                value: '3'
          - name: b4
            depends: b1
            template: B
            arguments:
              parameters:
              - name: msg
                value: '4'
          - name: b5
            depends: b2 && b3 && b4
            template: B
            arguments:
              parameters:
              - name: msg
                value: '5'
    ```

