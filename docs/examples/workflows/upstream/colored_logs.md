# Colored Logs

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/colored-logs.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Env, Workflow, script


    @script(image="python:3.7", add_cwd_to_sys_path=False, env=[Env(name="PYTHONUNBUFFERED", value="1")])
    def print_colors():
        import time  # noqa: I001
        import random

        messages = [
            "No Color",
            "\x1b[30m%s\x1b[0m" % "FG Black",
            "\x1b[32m%s\x1b[0m" % "FG Green",
            "\x1b[34m%s\x1b[0m" % "FG Blue",
            "\x1b[36m%s\x1b[0m" % "FG Cyan",
            "\x1b[41m%s\x1b[0m" % "BG Red",
            "\x1b[43m%s\x1b[0m" % "BG Yellow",
            "\x1b[45m%s\x1b[0m" % "BG Magenta",
        ]
        for i in range(1, 100):
            print(random.choice(messages))
            time.sleep(1)


    with Workflow(generate_name="colored-logs-", entrypoint="print-colors") as w:
        print_colors(name="print-colors")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: colored-logs-
    spec:
      entrypoint: print-colors
      templates:
      - name: print-colors
        script:
          image: python:3.7
          source: |-
            import time
            import random
            messages = ['No Color', '\x1b[30m%s\x1b[0m' % 'FG Black', '\x1b[32m%s\x1b[0m' % 'FG Green', '\x1b[34m%s\x1b[0m' % 'FG Blue', '\x1b[36m%s\x1b[0m' % 'FG Cyan', '\x1b[41m%s\x1b[0m' % 'BG Red', '\x1b[43m%s\x1b[0m' % 'BG Yellow', '\x1b[45m%s\x1b[0m' % 'BG Magenta']
            for i in range(1, 100):
                print(random.choice(messages))
                time.sleep(1)
          command:
          - python
          env:
          - name: PYTHONUNBUFFERED
            value: '1'
    ```

