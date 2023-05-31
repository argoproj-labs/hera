from hera.workflows import Steps, Workflow, script


@script()
def test_key_mapping(key_1: str, key_2: str):  # pragma: no cover
    print(f"{key_1}:{key_2}")


with Workflow(
    generate_name="loops-maps-",
    entrypoint="loop-map-example",
) as w:
    with Steps(name="loop-map-example") as loop_map_example:
        test_key_mapping(
            with_items=[
                {"key_1": "value:1-1", "key_2": "value:2-1"},
                {"key_1": "value:1-2", "key_2": "value:2-2"},
                {"key_1": "value:1-3", "key_2": "value:2-3"},
                {"key_1": "value:1-4", "key_2": "value:2-4"},
            ],
        )
