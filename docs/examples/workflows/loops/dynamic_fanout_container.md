# Dynamic Fanout Container



This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. Differ from dynamic_fanout.py, this example uses a container to generate the tasks and the dynamically
created tasks are also container only.
More details can be found here: https://github.com/argoproj-labs/hera-workflows/issues/250


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    generate = Container(
        name="generate",
        image="alpine:latest",
        command=["echo", '[{"value": "a"}, {"value": "b"}, {"value": "c"}]'],
    )

    fanout = Container(
        name="fanout",
        inputs=[Parameter(name="value")],
        image="alpine:latest",
        command=["echo", "{{inputs.parameters.value}}"],
    )

    # assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
    with Workflow(generate_name="dynamic-fanout-container-", entrypoint="d") as w:
        with DAG(name="d"):
            # this can be anything! e.g. fetch from some API, then in parallel process all entities; chunk database records
            # and process them in parallel, etc.
            g = generate()
            f = fanout(
                arguments={"value": "{{item.value}}"}, with_param=g.result
            )  # this make the task fan out over the `with_param`
            g >> f
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-fanout-container-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: generate
            template: generate
          - name: fanout
            depends: generate
            template: fanout
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: value
                value: '{{item.value}}'
      - name: generate
        container:
          image: alpine:latest
          command:
          - echo
          - '[{"value": "a"}, {"value": "b"}, {"value": "c"}]'
      - name: fanout
        container:
          image: alpine:latest
          command:
          - echo
          - '{{inputs.parameters.value}}'
        inputs:
          parameters:
          - name: value
    ```

