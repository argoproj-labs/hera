# Coinflip Recursive

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/coinflip-recursive.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow, script


    @script(image="python:alpine3.6", command=["python"], add_cwd_to_sys_path=False)
    def flip_coin() -> None:
        import random

        result = "heads" if random.randint(0, 1) == 0 else "tails"
        print(result)


    with Workflow(
        generate_name="coinflip-recursive-",
        entrypoint="coinflip",
    ) as w:
        heads = Container(
            name="heads",
            image="alpine:3.6",
            command=["sh", "-c"],
            args=['echo "it was heads"'],
        )

        with Steps(name="coinflip") as s:
            fc: Step = flip_coin()

            with s.parallel():
                heads(when=f"{fc.result} == heads")
                Step(name="tails", template=s, when=f"{fc.result} == tails")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: coinflip-recursive-
    spec:
      entrypoint: coinflip
      templates:
      - container:
          args:
          - echo "it was heads"
          command:
          - sh
          - -c
          image: alpine:3.6
        name: heads
      - name: coinflip
        steps:
        - - name: flip-coin
            template: flip-coin
        - - name: heads
            template: heads
            when: '{{steps.flip-coin.outputs.result}} == heads'
          - name: tails
            template: coinflip
            when: '{{steps.flip-coin.outputs.result}} == tails'
      - name: flip-coin
        script:
          command:
          - python
          image: python:alpine3.6
          source: 'import random

            result = ''heads'' if random.randint(0, 1) == 0 else ''tails''

            print(result)'
    ```

