# Suspend






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Parameter, Suspend, Workflow

    with Workflow(generate_name="suspend-", entrypoint="suspend-without-duration") as w:
        Suspend(name="suspend-without-duration")
        Suspend(name="suspend-with-duration", duration=30)
        Suspend(
            name="suspend-with-intermediate-param-enum",
            intermediate_parameters=[Parameter(name="approve", enum=["YES", "NO"], default="NO")],
        )
        Suspend(
            name="suspend-with-intermediate-param",
            intermediate_parameters=[Parameter(name="approve")],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: suspend-
    spec:
      entrypoint: suspend-without-duration
      templates:
      - name: suspend-without-duration
        suspend: {}
      - name: suspend-with-duration
        suspend:
          duration: '30'
      - name: suspend-with-intermediate-param-enum
        inputs:
          parameters:
          - name: approve
            default: 'NO'
            enum:
            - 'YES'
            - 'NO'
        outputs:
          parameters:
          - name: approve
            valueFrom:
              supplied: {}
        suspend: {}
      - name: suspend-with-intermediate-param
        inputs:
          parameters:
          - name: approve
        outputs:
          parameters:
          - name: approve
            valueFrom:
              supplied: {}
        suspend: {}
    ```

