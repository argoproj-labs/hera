from hera.shared.serialization import serialize
from hera.workflows import Steps, Workflow, script


@script()
def print_message(message):
    print(message)


with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
    with Steps(name="loop-example"):
        # We can pass a list of values to `with_items`
        print_message(
            name="print-message-loop-with-items-list",
            arguments={"message": "{{item}}"},
            with_items=["hello world", "goodbye world"],
        )

        # Or we can skip the arguments kwarg and string templating
        # syntax by passing a list of dictionaries
        print_message(
            name="print-message-loop-with-items-dict",
            with_items=[
                {"message": "hello world"},
                {"message": "goodbye world"},
            ],
        )

        # We can still pass a list of dict values to `with_items`, but must serialize them
        print_message(
            name="print-message-loop-with-items-list-of-dicts",
            arguments={"message": "{{item}}"},
            with_items=[serialize(item) for item in [{"my-key": "hello world"}, {"my-other-key": "goodbye world"}]],
        )
