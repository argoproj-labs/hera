# Template Sets



This example shows how to use the Hera concept of TemplateSet.

A TemplateSet lets you write templates that are not attached to a particular Workflow. You can then add the TemplateSet
to a Workflow at submission time. This can be useful if you just want to distribute Python packages. Read more in the
[Best Practices guide](../../../user-guides/best-practices.md)!


=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Output, TemplateSet, Workflow

    global_config.experimental_features["decorator_syntax"] = True

    w = Workflow(name="workflow-using-template-sets")
    templates = TemplateSet()


    @templates.script()
    def setup() -> Output:
        return Output(result="Setting things up")


    @templates.dag()
    def my_dag():
        setup(name="task-a")
        setup(name="task-b")


    w.add_template_set(templates)
    w.set_entrypoint(my_dag)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: workflow-using-template-sets
    spec:
      entrypoint: my-dag
      templates:
      - name: setup
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.template_sets:setup
          command:
          - python
          env:
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
      - name: my-dag
        dag:
          tasks:
          - name: task-a
            template: setup
          - name: task-b
            template: setup
    ```

