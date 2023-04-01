# Global Config






=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Container, Workflow, script

    global_config.api_version = "argoproj.io/v0beta9000"
    global_config.namespace = "argo-namespace"
    global_config.service_account_name = "argo-account"
    global_config.image = "image-say"
    global_config.script_command = ["python3"]


    @script()
    def say():
        print("hello")


    with Workflow(generate_name="global-config-", entrypoint="whalesay") as w:
        whalesay = Container(image="docker/whalesay:latest", command=["cowsay"])
        say()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v0beta9000
    kind: Workflow
    metadata:
      generateName: global-config-
      namespace: argo-namespace
    spec:
      entrypoint: whalesay
      serviceAccountName: argo-account
      templates:
      - container:
          command:
          - cowsay
          image: docker/whalesay:latest
      - name: say
        script:
          command:
          - python3
          image: image-say
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print("hello")

            '
    ```

