# Loops

A template can loop over a list of values using a Task or Step within a `DAG` or `Steps` context. There are three
looping constructs:

* `with_items` loops over a hard-coded list of values
* `with_param` loops over a parameter (dynamically)
* `with_sequence` loops over a list of numbers (similar to Python's `range` function)

The values in a list for `with_item` or `with_param` can be plain single values, referenced as `{{item}}`, or a
dictionary of values, where the elements in the dictionary can be addressed by its key as `{{item.key}}`.

A looped template will actually run in parallel for all the items: the items will be launched sequentially but the
running times may overlap. If you do not want to loop over the items in parallel, you should use a
[Synchronization](https://argoproj.github.io/argo-workflows/synchronization/) mechanism; see the
[Sequential Steps example](../examples/workflows/upstream/loops_arbitrary_sequential_steps.md).

## Basic `with_items` Usage

We can demonstrate basic `with_items` usage on the Hello World example:

```py
@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})
```

We can loop over a list of values passed to `with_items`, and pass `"{{item}}"` to the argument:

=== "Hera"

    ```py
    with Workflow(
        generate_name="hello-world-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            echo(
                arguments={"message": "{{item}}"},
                with_items=["Hello world!", "I'm looping!", "Goodbye world!"],
            )
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: echo
            template: echo
            withItems:
            - Hello world!
            - I'm looping!
            - Goodbye world!
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```

=== "Logs"

    ```console
    hello-world-9cf9j-echo-3186990983: Hello world!
    hello-world-9cf9j-echo-4182774221: I'm looping!
    hello-world-9cf9j-echo-1812072106: Goodbye world!
    ```

## Dictionary `with_items` Usage

You can pass a list of dictionaries to `with_items`, and reference keys in the dictionary with `"{{item.key}}"`. Note
that the keys must match across all the dictionaries.

=== "Hera"

    ```py
        @script()
        def message(message: str, times: int):
            for _ in range(times):
                print(message)

        with Workflow(
            generate_name="dictionary-items-",
            entrypoint="steps",
        ) as w:
            with Steps(name="steps"):
                message(
                    arguments={
                        "message": "{{item.msg}}",
                        "times": "{{item.n}}",
                    }
                    with_items=[
                        {
                            "msg": "Hello",
                            "n": 3,
                        },
                        {
                            "msg": "goodbye",
                            "n": 1,
                        },
                    ],
                )
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dictionary-items-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: message
            template: message
            withItems:
            - message: Hello
              times: 3
            - message: goodbye
              times: 1
            arguments:
              parameters:
              - name: message
                value: '{{item.message}}'
              - name: times
                value: '{{item.times}}'
      - name: message
        inputs:
          parameters:
          - name: message
          - name: times
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''
            try: times = json.loads(r'''{{inputs.parameters.times}}''')
            except: times = r'''{{inputs.parameters.times}}'''

            for _ in range(times):
                print(message)
          command:
          - python
    ```

=== "Logs"

    ```console
    dictionary-items-97w57-message-3427061660: Hello
    dictionary-items-97w57-message-3427061660: Hello
    dictionary-items-97w57-message-3427061660: Hello
    dictionary-items-97w57-message-3966219266: goodbye
    ```

Hera lets you omit the `arguments` passed to a Task or Step if all the keys match the function:

=== "Hera"

    ```py
    @script()
    def echo(foo: str, bar: int):
        print(foo, bar)

    with Workflow(
        generate_name="dictionary-items-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            echo(
                with_items=[
                    {
                        "foo": "Hello",
                        "bar": 42,
                    },
                    {
                        "foo": "world",
                        "bar": 42,
                    },
                ],
            )
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dictionary-items-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: func
            template: func
            withItems:
            - bar: 42
              foo: Hello
            - bar: 42
              foo: world
            arguments:
              parameters:
              - name: foo
                value: '{{item.foo}}'
              - name: bar
                value: '{{item.bar}}'
      - name: func
        inputs:
          parameters:
          - name: foo
          - name: bar
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: bar = json.loads(r'''{{inputs.parameters.bar}}''')
            except: bar = r'''{{inputs.parameters.bar}}'''
            try: foo = json.loads(r'''{{inputs.parameters.foo}}''')
            except: foo = r'''{{inputs.parameters.foo}}'''

            print(foo, bar)
          command:
          - python
    ```

## Dynamic Fan-out Using `with_param`

### From the Result of a Previous Step

A convenient use of `with_param` is with the `result` (the stdout) of a previous Task or Step. Here, we generate a list
of random length and consume it in the subsequent task:

=== "Hera"

    ```py
    @script()
    def generate():
        import json
        import sys
        import random

        json.dump([i for i in range(random.randint(8, 12))], sys.stdout)


    @script()
    def consume(value: int):
        print("Received value: {value}!".format(value=value))


    with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generate()
            c = consume(with_param=g.result)
            g >> c
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-fanout-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: generate
            template: generate
          - name: consume
            depends: generate
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: value
                value: '{{item}}'
      - name: generate
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            json.dump([i for i in range(10)], sys.stdout)
          command:
          - python
      - name: consume
        inputs:
          parameters:
          - name: value
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: value = json.loads(r'''{{inputs.parameters.value}}''')
            except: value = r'''{{inputs.parameters.value}}'''

            print('Received value: {value}!'.format(value=value))
          command:
          - python
    ```

### From a Specific Output Parameter of a Previous Step

If a previous step outputs a JSON-serialised list, you can loop over it using `get_parameter` from that step:

```py
@script(outputs=[Parameter(name="task-output", value_from=ValueFrom(path="/tmp/output.json"))])
def generate():
    import json

    with open("/tmp/output.json", "w") as f:
        json.dump([i for i in range(10)], f)


@script()
def consume(value: int):
    print("Received value: {value}!".format(value=value))


with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        c = consume(with_param=g.get_parameter("task-output"))
        g >> c
```

### From a Steps or DAG context

You can loop over an input parameter of a `Steps` or `DAG` context using `get_parameter`. In this Workflow, Argo will
pass the `arguments` from the `Workflow` into the `Steps` template:

=== "Hera"

    ```py
    @script()
    def consume(value: int):
        print("Received value: {value}!".format(value=value))


    with Workflow(
        generate_name="step-fanout-",
        entrypoint="d",
        arguments={"step-input": [1, 2, 3]},
    ) as w:
        with Steps(name="d", inputs=[Parameter(name="step-input")]) as s:
            c = consume(with_param=s.get_parameter("step-input"))
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: step-fanout-
    spec:
      entrypoint: d
      templates:
      - name: d
        steps:
        - - name: consume
            template: consume
            withParam: '{{inputs.parameters.step-input}}'
            arguments:
              parameters:
              - name: value
                value: '{{item}}'
        inputs:
          parameters:
          - name: step-input
      - name: consume
        inputs:
          parameters:
          - name: value
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: value = json.loads(r'''{{inputs.parameters.value}}''')
            except: value = r'''{{inputs.parameters.value}}'''

            print('Received value: {value}!'.format(value=value))
          command:
          - python
      arguments:
        parameters:
        - name: step-input
          value: '[1, 2, 3]'
    ```

## Aggregating Loop Results (Fan-In)

After a loop (also known as a "fan-out"), you can collect the results together in the next step (known as a "fan-in") as
a list:

=== "Hera"

    ```py
    @script()
    def generate():
        import json
        import sys

        json.dump([{"value": i} for i in range(10)], sys.stdout)


    @script(outputs=[Parameter(name="value", value_from=ValueFrom(path="/tmp/value"))])
    def fanout(object: dict):
        print("Received object: {object}!".format(object=object))
        # Output the content of the "value" key in the object
        value = object["value"]
        with open("/tmp/value", "w") as f:
            f.write(str(value))


    @script()
    def fanin(values: list):
        print("Received values: {values}!".format(values=values))


    with Workflow(generate_name="dynamic-fanout-fanin", entrypoint="d") as w:
        with DAG(name="d"):
            gen_task = generate()
            fanout_task = fanout(with_param=gen_task.result)
            fanin_task = fanin(arguments=fanout_task.get_parameter("value").with_name("values"))
            gen_task >> fanout_task >> fanin_task
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-fanout-fanin
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: generate
            template: generate
          - name: fanout
            depends: generate
            template: fanout
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: object
                value: '{{item}}'
          - name: fanin
            depends: fanout
            template: fanin
            arguments:
              parameters:
              - name: values
                value: '{{tasks.fanout.outputs.parameters.value}}'
      - name: generate
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            json.dump([{'value': i} for i in range(10)], sys.stdout)
          command:
          - python
      - name: fanout
        inputs:
          parameters:
          - name: object
        outputs:
          parameters:
          - name: value
            valueFrom:
              path: /tmp/value
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: object = json.loads(r'''{{inputs.parameters.object}}''')
            except: object = r'''{{inputs.parameters.object}}'''

            print('Received object: {object}!'.format(object=object))
            value = object['value']
            with open('/tmp/value', 'w') as f:
                f.write(str(value))
          command:
          - python
      - name: fanin
        inputs:
          parameters:
          - name: values
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: values = json.loads(r'''{{inputs.parameters.values}}''')
            except: values = r'''{{inputs.parameters.values}}'''

            print('Received values: {values}!'.format(values=values))
          command:
          - python
    ```

## Using `with_sequence`

The use case for `with_sequence` is quite narrow, so you will probably not use it that frequently. Here, we show how the
`count` value can come from another task output, and that `"{{item}}"` is used in the same way as `with_items` and
`with_param`:

=== "Hera"

    ```py
    @script()
    def gen_num():
        print(3)


    @script()
    def say(message: str):
        print(message)


    with Workflow(generate_name="with-sequence-example", entrypoint="d") as w:
        with DAG(name="d"):
            t1 = gen_num(name="t1")
            t2 = say(name="t2", with_sequence=Sequence(count=t1.result, start="0"), arguments={"message": "{{item}}"})
            t1 >> t2
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: with-sequence-example
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: t1
            template: gen-num
          - name: t2
            depends: t1
            template: say
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
            withSequence:
              count: '{{tasks.t1.outputs.result}}'
              start: '0'
      - name: gen-num
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print(3)
          command:
          - python
      - name: say
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```
