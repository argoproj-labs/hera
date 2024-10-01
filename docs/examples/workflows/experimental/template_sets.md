# Template Sets






=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Output, TemplateSet, Workflow

    global_config.experimental_features["decorator_syntax"] = True

    w = Workflow(name="my-workflow")
    templates = TemplateSet()


    @templates.script()
    def setup() -> Output:
        return Output(result="Setting things up")


    @templates.dag()
    def my_dag():
        setup(name="task-a")
        setup(name="task-b")


    w.add_template_set(templates)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: my-workflow
    spec:
      templates:
      - name: setup
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.template_sets:setup
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__outputs_directory
            value: /tmp/hera-outputs
          - name: hera__script_pydantic_io
            value: ''
          image: python:3.9
          source: '{{inputs.parameters}}'
      - dag:
          tasks:
          - name: task-a
            template: setup
          - name: task-b
            template: setup
        name: my-dag
    ```

