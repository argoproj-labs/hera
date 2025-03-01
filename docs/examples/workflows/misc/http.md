# Http






=== "Hera"

    ```python linenums="1"
    from hera.expr import g
    from hera.workflows import HTTP, Parameter, Workflow

    with Workflow(generate_name="http-", entrypoint="http") as w:
        HTTP(
            name="http",
            inputs=[Parameter(name="url", value="https://example.com")],
            timeout_seconds=20,
            url=f"{g.inputs.parameters.url:$}",
            method="GET",
            headers=[{"name": "x-header-name", "value": "test-value"}],
            success_condition=str(g.response.body.contains("google")),  # type: ignore
            body="test body",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: http-
    spec:
      entrypoint: http
      templates:
      - name: http
        http:
          body: test body
          method: GET
          successCondition: response.body contains 'google'
          timeoutSeconds: 20
          url: '{{inputs.parameters.url}}'
          headers:
          - name: x-header-name
            value: test-value
        inputs:
          parameters:
          - name: url
            value: https://example.com
    ```

