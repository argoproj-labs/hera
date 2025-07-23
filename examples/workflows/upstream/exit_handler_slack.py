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
