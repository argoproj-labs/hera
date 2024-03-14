# Testing Templates And Workflows






=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import DAG, RunnerScriptConstructor, Script, Workflow, WorkflowsService, script

    try:
        from pydantic.v1 import BaseModel
    except ImportError:
        from pydantic import BaseModel

    global_config.set_class_defaults(Script, constructor=RunnerScriptConstructor())


    class Rectangle(BaseModel):
        length: float
        width: float

        def area(self) -> float:
            return self.length * self.width


    @script(constructor="runner", image="my-built-python-image")
    def calculate_area_of_rectangle(rectangle: Rectangle) -> float:
        return rectangle.area()


    with Workflow(
        generate_name="dag-",
        entrypoint="dag",
        namespace="argo",
        workflows_service=WorkflowsService(host="https://localhost:2746"),
    ) as w:
        with DAG(name="dag"):
            A = calculate_area_of_rectangle(
                name="rectangle-1", arguments={"rectangle": Rectangle(length=1.2, width=3.4).json()}
            )
            B = calculate_area_of_rectangle(
                name="rectangle-2", arguments={"rectangle": Rectangle(length=4.3, width=2.1).json()}
            )
            A >> B


    def test_calculate_area_of_rectangle():
        r = Rectangle(length=2.0, width=3.0)
        assert calculate_area_of_rectangle(r) == 6.0


    def test_create_workflow():
        model_workflow = w.create(wait=True)
        assert model_workflow.status and model_workflow.status.phase == "Succeeded"

        echo_node = next(
            filter(
                lambda n: n.display_name == "echo",
                model_workflow.status.nodes.values(),
            )
        )
        assert echo_node.outputs.parameters[0].value == "my value"
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-
      namespace: argo
    spec:
      entrypoint: dag
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: rectangle
                value: '{"length": 1.2, "width": 3.4}'
            name: rectangle-1
            template: calculate-area-of-rectangle
          - arguments:
              parameters:
              - name: rectangle
                value: '{"length": 4.3, "width": 2.1}'
            depends: rectangle-1
            name: rectangle-2
            template: calculate-area-of-rectangle
        name: dag
      - inputs:
          parameters:
          - name: rectangle
        name: calculate-area-of-rectangle
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.use_cases.testing_templates_and_workflows:calculate_area_of_rectangle
          command:
          - python
          image: my-built-python-image
          source: '{{inputs.parameters}}'
    ```

