# Loops Maps

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/loops-maps.yaml).



## Hera

```python
from hera.workflows import Workflow, Container, Steps, Parameter

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
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: loops-maps-
spec:
  entrypoint: loop-map-example
  templates:
  - container:
      args:
      - /etc/os-release
      command:
      - cat
      image: '{{inputs.parameters.image}}:{{inputs.parameters.tag}}'
    inputs:
      parameters:
      - name: image
      - name: tag
    name: cat-os-release
  - name: loop-map-example
    steps:
    - - arguments:
          parameters:
          - name: image
            value: '{{item.image}}'
          - name: tag
            value: '{{item.tag}}'
        name: test-linux
        template: cat-os-release
        withItems:
        - image: debian
          tag: '9.1'
        - image: debian
          tag: '8.9'
        - image: alpine
          tag: '3.6'
        - image: ubuntu
          tag: '17.10'
```
