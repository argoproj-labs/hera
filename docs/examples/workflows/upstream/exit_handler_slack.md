# Exit Handler Slack

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-slack.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="exit-handler-slack-",
        entrypoint="say-hello",
        on_exit="exit-handler",
    ) as w:
        Container(
            name="say-hello",
            args=["echo hello"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        Container(
            name="exit-handler",
            args=[
                'curl -X POST --data-urlencode \'payload={ "text": "{{workflow.name}} finished", "blocks": [ { "type": "section", "text": { "type": "mrkdwn", "text": "Workflow {{workflow.name}} {{workflow.status}}", } } ] }\' YOUR_WEBHOOK_URL_HERE'
            ],
            command=["sh", "-c"],
            image="curlimages/curl",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: exit-handler-slack-
    spec:
      entrypoint: say-hello
      onExit: exit-handler
      templates:
      - name: say-hello
        container:
          image: alpine:latest
          args:
          - echo hello
          command:
          - sh
          - -c
      - name: exit-handler
        container:
          image: curlimages/curl
          args:
          - 'curl -X POST --data-urlencode ''payload={ "text": "{{workflow.name}} finished",
            "blocks": [ { "type": "section", "text": { "type": "mrkdwn", "text": "Workflow
            {{workflow.name}} {{workflow.status}}", } } ] }'' YOUR_WEBHOOK_URL_HERE'
          command:
          - sh
          - -c
    ```

