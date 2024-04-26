# Dynamic Resources



This example showcases how to compute dynamic resources for a step/task and pass them through.

This is useful when you write workflows in a business context that requires processing some data dynamically. For
example, if you have a step that performs QC checks on some data, and only a subset of the data passes the checks, then
you can compute the resources dynamically based on the amount of data you need to process in follow up steps.


=== "Hera"

    ```python linenums="1"
    import json

    from hera.workflows import DAG, Workflow, script


    @script(image="python:3.10")
    def compute_resources() -> None:
        """Computes the resources necessary by the following job, which could be anything."""
        import json
        import sys

        resources = []
        for i in range(1, 4):
            resources.append({"cpu": i, "mem": "{v}Mi".format(v=i * 100)})

        json.dump(resources, sys.stdout)


    @script(
        image="python:3.10",
        pod_spec_patch=json.dumps(
            {
                "containers": [
                    {
                        "name": "main",
                        "resources": {
                            "limits": {"cpu": "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"},
                            "requests": {"cpu": "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"},
                        },
                    }
                ]
            }
        ),
    )
    def resource_consumer(cpu: int, mem: str) -> None:
        """Perform some computation."""
        print("received cpu {cpu} and mem {mem}".format(cpu=cpu, mem=mem))


    @script(
        image="python:3.10",
        pod_spec_patch=json.dumps(
            {
                "containers": [
                    {
                        "name": "main",
                        "resources": {
                            "limits": {"cpu": "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"},
                            "requests": {"cpu": "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"},
                        },
                    }
                ]
            }
        ),
    )
    def another_resource_consumer(cpu: int = 1, mem: str = "100Mi") -> None:
        """Perform some computation."""
        print("received cpu {cpu} and mem {mem}".format(cpu=cpu, mem=mem))


    with Workflow(
        generate_name="dynamic-resources-",
        entrypoint="d",
    ) as w:
        with DAG(name="d"):
            c = compute_resources()
            # when you don't have kwargs set for a function like `resource_consumer` then Hera can infer that you
            # likely want to map the `resource_consumer` parameters to the `with_param` output of `generate_resources`!
            # This relies on the `with_param` field, as Hera needs to know there's some dynamic input to `resource_consumer`
            c >> resource_consumer(with_param=c.result)
            # by comparison, `another_resource_consumer` has kwargs set, so Hera will not infer that you want to map
            # the output of `generate_resources` to the inputs. Instead, it creates the kwargs for you, and lets you take
            # control of the mapping! This is because Hera cannot know whether you intend to map only 1 param, or all of
            # them, so it empowers you to set it!
            c >> another_resource_consumer(with_param=c.result, arguments={"cpu": "{{item.cpu}}", "mem": "{{item.mem}}"})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-resources-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: compute-resources
            template: compute-resources
          - arguments:
              parameters:
              - name: cpu
                value: '{{item.cpu}}'
              - name: mem
                value: '{{item.mem}}'
            depends: compute-resources
            name: resource-consumer
            template: resource-consumer
            withParam: '{{tasks.compute-resources.outputs.result}}'
          - arguments:
              parameters:
              - name: cpu
                value: '{{item.cpu}}'
              - name: mem
                value: '{{item.mem}}'
            depends: compute-resources
            name: another-resource-consumer
            template: another-resource-consumer
            withParam: '{{tasks.compute-resources.outputs.result}}'
        name: d
      - name: compute-resources
        script:
          command:
          - python
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            """Computes the resources necessary by the following job, which could be anything."""
            import json
            import sys
            resources = []
            for i in range(1, 4):
                resources.append({'cpu': i, 'mem': '{v}Mi'.format(v=i * 100)})
            json.dump(resources, sys.stdout)
      - inputs:
          parameters:
          - name: cpu
          - name: mem
        name: resource-consumer
        podSpecPatch: '{"containers": [{"name": "main", "resources": {"limits": {"cpu":
          "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"}, "requests":
          {"cpu": "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"}}}]}'
        script:
          command:
          - python
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: cpu = json.loads(r'''{{inputs.parameters.cpu}}''')
            except: cpu = r'''{{inputs.parameters.cpu}}'''
            try: mem = json.loads(r'''{{inputs.parameters.mem}}''')
            except: mem = r'''{{inputs.parameters.mem}}'''

            """Perform some computation."""
            print('received cpu {cpu} and mem {mem}'.format(cpu=cpu, mem=mem))
      - inputs:
          parameters:
          - default: '1'
            name: cpu
          - default: 100Mi
            name: mem
        name: another-resource-consumer
        podSpecPatch: '{"containers": [{"name": "main", "resources": {"limits": {"cpu":
          "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"}, "requests":
          {"cpu": "{{inputs.parameters.cpu}}", "memory": "{{inputs.parameters.mem}}"}}}]}'
        script:
          command:
          - python
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: cpu = json.loads(r'''{{inputs.parameters.cpu}}''')
            except: cpu = r'''{{inputs.parameters.cpu}}'''
            try: mem = json.loads(r'''{{inputs.parameters.mem}}''')
            except: mem = r'''{{inputs.parameters.mem}}'''

            """Perform some computation."""
            print('received cpu {cpu} and mem {mem}'.format(cpu=cpu, mem=mem))
    ```

