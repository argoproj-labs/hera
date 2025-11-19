# Steps

Steps are a simple way to sequentially run a series of templates. They can also be run in parallel, and conditionally by
using `when` clauses.

Basic `Steps` usage involves creating a `Steps` object as a context manager, and referencing template functions within
the context. When using a `@script` function multiple times under a single `Steps` context, you must pass in a unique
`name` (which becomes the *step's* name) for each call. Compare the Hera Workflow with YAML in the example below:

=== "Hera"

    ```py
    from hera.workflows import Steps, Workflow, script


    @script()
    def echo(message: str):
        print(message)


    with Workflow(
        generate_name="hello-world-steps-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            echo(name="hello", arguments={"message": "Hello world!"})
            echo(name="goodbye", arguments={"message": "Goodbye world!"})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-steps-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: hello
            template: echo
            arguments:
              parameters:
              - name: message
                value: Hello world!
        - - name: goodbye
            template: echo
            arguments:
              parameters:
              - name: message
                value: Goodbye world!
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.10
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

## Parallel Steps

You can run multiple Steps in parallel by creating a sub-context under a `Steps` context manager using its `parallel()`
function. We can create a set of parallel steps within a sequence of sequential steps, which we can see in this example:


===  "Hera"

    ```py
    from hera.workflows import Steps, Workflow, script


    @script()
    def echo(message: str):
        print(message)


    with Workflow(
        generate_name="hello-world-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps") as s:
            echo(name="pre-parallel", arguments={"message": "Hello world!"})

            with s.parallel():
                echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
                echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
                echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})

            echo(name="post-parallel", arguments={"message": "Goodbye world!"})
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
        - - name: pre-parallel
            template: echo
            arguments:
              parameters:
              - name: message
                value: Hello world!
        - - name: parallel-1
            template: echo
            arguments:
              parameters:
              - name: message
                value: I'm parallel-1!
          - name: parallel-2
            template: echo
            arguments:
              parameters:
              - name: message
                value: I'm parallel-2!
          - name: parallel-3
            template: echo
            arguments:
              parameters:
              - name: message
                value: I'm parallel-3!
        - - name: post-parallel
            template: echo
            arguments:
              parameters:
              - name: message
                value: Goodbye world!
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.10
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

Remember any parallel steps will run indeterminately within the context, so `parallel-1`, `parallel-2` and `parallel-3`
could run in any order, but `pre-parallel` will always run before the parallel steps and `post-parallel` will run after
*all* the parallel steps have completed.

## `when` Clauses

A `when` clause specifies the conditions under which the step or task will run. Examples of `when` clauses can be found
throughout the examples, such as [the Argo coinflip example](../examples/workflows/upstream/coinflip.md).

We can create a Workflow with identical behaviour to the upstream coinflip, but using only Python scripts and syntactic
sugar functions, which makes for more readable and maintainable code!

=== "Hera"

    ```py
    from hera.workflows import Steps, Workflow, script


    @script()
    def flip():
        import random

        result = "heads" if random.randint(0, 1) == 0 else "tails"
        print(result)


    @script()
    def it_was(coin_result):
        print(f"it was {coin_result}")


    with Workflow(generate_name="coinflip-", entrypoint="steps") as w:
        with Steps(name="steps") as s:
            f = flip()
            with s.parallel():
                it_was(name="heads", arguments={"coin_result": "heads"}, when=f'{f.result} == "heads"')
                it_was(name="tails", arguments={"coin_result": "tails"}, when=f'{f.result} == "tails"')
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: coinflip-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: flip
            template: flip
        - - name: heads
            template: it-was
            when: '{{steps.flip.outputs.result}} == "heads"'
            arguments:
              parameters:
              - name: coin_result
                value: heads
          - name: tails
            template: it-was
            when: '{{steps.flip.outputs.result}} == "tails"'
            arguments:
              parameters:
              - name: coin_result
                value: tails
      - name: flip
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            result = 'heads' if random.randint(0, 1) == 0 else 'tails'
            print(result)
          command:
          - python
      - name: it-was
        inputs:
          parameters:
          - name: coin_result
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: coin_result = json.loads(r'''{{inputs.parameters.coin_result}}''')
            except: coin_result = r'''{{inputs.parameters.coin_result}}'''

            print(f'it was {coin_result}')
          command:
          - python

    ```

<details><summary>Click to see an example Workflow log</summary>

```console
coinflip-gfrws-flip-1899249874: heads
coinflip-gfrws-it-was-2809981541: it was heads
```

</details>

For more about `when` clauses, see the [Conditionals](conditionals.md) walkthrough page.
