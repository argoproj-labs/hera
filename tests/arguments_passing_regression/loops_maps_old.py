from hera.workflows import Container, Parameter, Steps, Workflow

with Workflow(
    generate_name="loops-maps-",
    entrypoint="loop-map-example",
) as w:
    cat_os_release = Container(
        name="cat-os-release",
        inputs=[Parameter(name="image"), Parameter(name="tag")],
        image="{{inputs.parameters.image}}:{{inputs.parameters.tag}}",
        command=["cat"],
        args=["/etc/os-release"],
    )

    with Steps(name="loop-map-example") as loop_map_example:
        cat_os_release(
            name="test-linux",
            arguments=[
                Parameter(name="image", value="{{item.image}}"),
                Parameter(name="tag", value="{{item.tag}}"),
            ],
            with_items=[
                {"image": "debian", "tag": "9.1"},
                {"image": "debian", "tag": "8.9"},
                {"image": "alpine", "tag": "3.6"},
                {"image": "ubuntu", "tag": "17.10"},
            ],
        )
