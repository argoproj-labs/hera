# Meta
[meta]: #meta
- Name: YAML Code Converter
- Start Date: (fill in today's date: YYYY-MM-DD)
- Update date (optional): (fill in today's date: YYYY-MM-DD)
- Author(s): [@elliotgunton](https://github.com/elliotgunton)
- Supersedes: N/A

# Table of Contents
[table-of-contents]: #table-of-contents
- [Meta](#meta)
- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Definitions](#definitions)
- [Motivation](#motivation)
- [Proposal](#proposal)
  - [Terminology](#terminology)
  - [Code Examples](#code-examples)
  - [How to teach (OPTIONAL)](#how-to-teach-optional)
- [Implementation (OPTIONAL)](#implementation-optional)
  - [Link to the Implementation PR](#link-to-the-implementation-pr)
- [Migration (OPTIONAL)](#migration-optional)
- [Drawbacks](#drawbacks)
- [Alternatives](#alternatives)
- [Prior Art](#prior-art)
- [Unresolved Questions (OPTIONAL)](#unresolved-questions-optional)

# Overview
[overview]: #overview

This HEP introduces a way to generate boilerplate Hera code from existing YAML Workflows, allowing existing Argo Workflows users to get their adoption of Hera kick started.

# Definitions
[definitions]: #definitions

Make a list of the definitions that may be useful for those reviewing. Include phrases and words that Hera users or other interested parties may not be familiar with.

# Motivation
[motivation]: #motivation

We've seen high demand from the community for this feature, see [issue 711](https://github.com/argoproj-labs/hera/issues/711) with support and comments (plus some duplicate issues being added). Issue #711 provides a great write-up (credit to [Leewaldoe](https://github.com/Leewaldoe)) for motivating this feature, so I will copy it here:

> The problem is that currently, there is no straightforward way to convert Argo yaml files to Hera code. This can be a time-consuming process, especially for large or complex workflows and for those more familiar with yaml but would like to start using Hera.
>
> The current alternative to this feature is to manually convert Argo yaml files to Hera code. This involves going through examples, understanding the mapping between yaml and Hera syntax, and spending hours rewriting and testing the code. However, this process is time-consuming, labor-intensive, and prone to human error. It also requires a deep understanding of both yaml and Hera, which might be a barrier for some users.
>
> I would like a feature that can automatically convert Argo yaml files into equivalent Hera code. This would involve parsing the yaml file, interpreting its structure and contents, and generating corresponding Hera code that represents the same workflow.
>
> Adding this feature would not only simplify the process of creating and managing Argo workflows but also provide the following benefits:
> * It would make it easier for users to transition from using pure yaml to Hera. By providing a way to automatically convert their existing Argo yaml files into Hera code, we can lower the barrier to entry and encourage more users to adopt Hera.
> * It would increase the speed of understanding Hera for those coming from a pure yaml implementation. By seeing how their familiar YAML workflows translate into Hera code, users can more quickly grasp the structure and syntax of Hera, accelerating their learning process.
>
> This feature would serve as a valuable tool for onboarding new users to Hera.

# Proposal
 
The proposed solution is to generate the corresponding Hera code for the given workflow YAML. This means using the hand-crafted wrapper classes, *not* the generated model classes. We want the generated code to be readable and mirror best practices, so we should use Workflow, DAG and Steps contexts where possible, as well as the `@script` decorator for "inline" Python templates.

The decorators added in [HEP 0001](0001-decorators.md) offer a way for us to generate stub functions for all the main template types (Scripts, Containers, DAGs and Steps), but as it is not feature complete (in terms of matching Argo YAML), we cannot use it with a guarantee of being able to generate any Argo Workflow, which we can in theory with a combination of Hera and model code.

We should be able to build the feature in the Hera CLI, such that the command would be:

```
hera generate python --from <yaml-file> [--to <filepath>]
```

which would take in a YAML file and generate the Python code to stdout, or the file if provided.

This would be a destructive operation, i.e. we would not consider if the file exists and contains code already. This is because we want to generate boilerplate for the user to build on, rather than interpreting what they already have, which would probably more than double the effort of implementation (being able to read and interpret the existing code, vs generating templated boilerplate from the YAML). This way, we can progressively build the Python code generator, such as generating Containers-only first, then DAGs, scripts, etc.

## Terminology

Define any new terminology.


## Code Examples

The existing examples collection show the forward translation, from Python to YAML, so we can consider the reverse
translation, generating the same Python from the YAML. However, for script template functions in particular, we add some
boilerplate code to inline scripts, importing `os` and `sys`, and we read in the input parameters via `json.loads`, so
we will likely not use the special `@script` decorator for script templates, especially as they wouldn't have been
written with Hera.

We can probably have a test to run on all the YAML examples to create (temporary) Python files, and then see if they
generate the same YAML. Some specific examples are collected below:

### Containers

Consider the basic hello world example using containers, with no parameters etc

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
  labels:
    workflows.argoproj.io/archive-strategy: "false"
  annotations:
    workflows.argoproj.io/description: |
      This is a simple hello world example.
spec:
  entrypoint: hello-world
  templates:
  - name: hello-world
    container:
      image: busybox
      command: [echo]
      args: ["hello world"]

```

We should be able to generate the following Python code:

```py
from hera.workflows import Container, Workflow

with Workflow(
    generate_name="hello-world-",
    entrypoint="hello-world",
    labels={
      "workflows.argoproj.io/archive-strategy": "false",
    },
    annotations={
      "workflows.argoproj.io/description": "This is a simple hello world example."
    }
) as w:
    Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
```

### Parameters

We can consider a template with an input.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: echo-message-
spec:
  entrypoint: echo-message
  arguments:
    - name: message
      value: test
  templates:
  - name: echo-message
    inputs:
      - name: message
    container:
      image: busybox
      command: [echo]
      args: ["{{inputs.parameters.message}}"]

```

We should be able to generate the following Python code:

```py
from hera.workflows import Container, Workflow

with Workflow(
    generate_name="hello-world-",
    entrypoint="hello-world",
    arguments={
      "echo-message": "test",
    }
) as w:
    Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
    )
```

### DAGs

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: dag-diamond-
spec:
  entrypoint: diamond
  templates:
  - name: diamond
    dag:
      tasks:
      - name: A
        template: echo
        arguments:
          parameters: [{name: message, value: A}]
      - name: B
        depends: "A"
        template: echo
        arguments:
          parameters: [{name: message, value: B}]
      - name: C
        depends: "A"
        template: echo
        arguments:
          parameters: [{name: message, value: C}]
      - name: D
        depends: "B && C"
        template: echo
        arguments:
          parameters: [{name: message, value: D}]
  - name: echo
    inputs:
      parameters:
      - name: message
    container:
      image: alpine:3.7
      command: [echo, "{{inputs.parameters.message}}"]
```

```py
from hera.workflows import DAG, Container, Parameter, Workflow

with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D
```

### Steps

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: steps-
spec:
  entrypoint: hello-hello-hello
  templates:
  - name: hello-hello-hello
    steps:
    - - name: hello1
        template: print-message
        arguments:
          parameters: [{name: message, value: "hello1"}]
    - - name: hello2a
        template: print-message
        arguments:
          parameters: [{name: message, value: "hello2a"}]
      - name: hello2b
        template: print-message
        arguments:
          parameters: [{name: message, value: "hello2b"}]
  - name: print-message
    inputs:
      parameters:
      - name: message
    container:
      image: busybox
      command: [echo]
      args: ["{{inputs.parameters.message}}"]
```

```py
from hera.workflows import Container, Parameter, Step, Steps, Workflow

with Workflow(
    generate_name="steps-",
    entrypoint="hello-hello-hello",
) as w:
    print_message = Container(
        name="print-message",
        inputs=[Parameter(name="message")],
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="hello-hello-hello") as s:
        Step(
            name="hello1",
            template=print_message,
            arguments=[Parameter(name="message", value="hello1")],
        )

        with s.parallel():
            Step(
                name="hello2a",
                template=print_message,
                arguments=[Parameter(name="message", value="hello2a")],
            )
            Step(
                name="hello2b",
                template=print_message,
                arguments=[Parameter(name="message", value="hello2b")],
            )
```

### Scripts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: scripts-python-
spec:
  entrypoint: python-script-example
  templates:
  - name: python-script-example
    steps:
    - - name: generate
        template: gen-random-int
    - - name: print
        template: print-message
        arguments:
          parameters:
          - name: message
            value: "{{steps.generate.outputs.result}}"

  - name: gen-random-int
    script:
      image: python:alpine3.6
      command: [python]
      source: |
        import random
        i = random.randint(1, 100)
        print(i)

  - name: print-message
    inputs:
      parameters:
      - name: message
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["echo result was: {{inputs.parameters.message}}"]
```

```py
from hera.workflows import Container, Parameter, Script, Step, Steps, Workflow

with Workflow(
    generate_name="scripts-python-",
    entrypoint="python-script-example",
) as w:
    gen_random_int = Script(
        name="gen-random-int",
        image="python:alpine3.6",
        command=["python"],
        source="""
import random
i = random.randint(1, 100)
print(i)""",
    )

    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo result was: {{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )

    with Steps(name="python-script-example") as s:
        Step(
            name="generate",
            template="gen-random-int",
        )
        Step(
            name="print",
            template="print-message",
            arguments={"message": "{{steps.generate.outputs.result}}"},
        )
```


# Implementation

We will give a proof-of-concept for generating Python code from basic Containers/DAG YAMLs, which can be expanded on for the remaining fields from the API and other template types.

## Link to the Implementation PR

POC for generating Containers and DAGs to begin with.

# Migration (OPTIONAL)

This section should document breaks to public API and breaks in compatibility due to this HEP's proposed changes. In addition, it should document the proposed steps that one would need to take to work through these changes.

# Drawbacks

Why should we **not** do this?

# Alternatives

- What other designs have been considered?
- Why is this proposal the best?
- What is the impact of not doing this?

# Prior Art

Discuss [prior art](https://en.wikipedia.org/wiki/Prior_art), both the good and bad.

# Unresolved Questions (OPTIONAL)

- What parts of the design do you expect to be resolved before this gets merged?
- What parts of the design do you expect to be resolved through implementation of the feature?
- What related issues do you consider out of scope for this HEP that could be addressed in the future independently of the solution that comes out of this HEP?
