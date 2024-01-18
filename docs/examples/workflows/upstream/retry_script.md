# Retry Script

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-script.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import RetryStrategy, Workflow, script


    @script(image="python:alpine3.6", retry_strategy=RetryStrategy(limit="10"), add_cwd_to_sys_path=False)
    def retry_script():
        import random
        import sys

        exit_code = random.choice([0, 1, 1])
        sys.exit(exit_code)


    with Workflow(generate_name="retry-script-", entrypoint="retry-script") as w:
        retry_script()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-script-
    spec:
      entrypoint: retry-script
      templates:
      - name: retry-script
        retryStrategy:
          limit: '10'
        script:
          command:
          - python
          image: python:alpine3.6
          source: |-
            import random
            import sys
            exit_code = random.choice([0, 1, 1])
            sys.exit(exit_code)
    ```

