"""This example shows how Hera can automatically map the values in a `with_items` dictionary.

See how to do this dynamically in the [JSON payload fanout](json_payload_fanout.md) example.
"""

from hera.workflows import Steps, Workflow, script


@script()
def test_key_mapping(key_1: str, key_2: str):
    print("{key_1}, {key_2}".format(key_1=key_1, key_2=key_2))


with Workflow(
    generate_name="script-argument-mapping-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        test_key_mapping(
            with_items=[
                {"key_1": "value:1-1", "key_2": "value:2-1"},
                {"key_1": "value:1-2", "key_2": "value:2-2"},
                {"key_1": "value:1-3", "key_2": "value:2-3"},
                {"key_1": "value:1-4", "key_2": "value:2-4"},
            ],
        )
