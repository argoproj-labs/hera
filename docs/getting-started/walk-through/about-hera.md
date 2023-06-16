# About

Hera is a Python library that allows you to construct and submit Argo Workflows. It is designed to be intuitive and easy
to use, while also providing a powerful interface to the underlying Argo API.

Hera acts as a domain-specific-language on top of Argo, so it is primarily a way to define Workflows. In previous Argo
Workflows surveys such as [2021](https://blog.argoproj.io/argo-workflows-2021-survey-results-d6fa890030ee), a better
Python DSL has been highly requested to overcome the YAML barrier to adoption. In the
[2022 survey results](https://blog.argoproj.io/cncf-argo-project-2022-user-survey-results-f9caf46df7fd#:~:text=Job%20Roles%20%26%20Use%20Cases)
we can infer from the job roles for people using Argo Workflows that the DevOps Engineers are likely more comfortable
using YAML than ML Engineers.

> * DevOps Engineers: 41%
> * Software Engineer: 20%
> * Architects: 20%
> * Data Engineer / Data Scientist / ML Engineer: 13%

We hope by providing a more intuitive Python definition language, Data and ML users of Argo Workflows will increase.

## Feature Parity

A natural concern about an abstraction layer on top of another technology is whether it can function the same as the
original lower layer. In this case, Hera generates a [library of model classes](../../api/workflows/models.md) using
Argo's OpenAPI spec which are wrapped up by Hera's feature-rich classes, while the model classes are available as a
fallback mechanism. You can check out the extensive
["upstream" examples](../../examples/workflows/upstream/dag_diamond.md) that contain side-by-side Python and YAML
definitions for Workflows in
[the Argo examples folder on GitHub](https://github.com/argoproj/argo-workflows/tree/master/examples). Our CI/CD runs
through the Argo examples folder to check that we are able to reproduce them using Hera Workflows written by hand (note:
we have not _yet_ written Hera Workflows for all the examples).

If you are a new user of Argo, we encourage you to become familiar with
[Argo's Core Concepts](https://argoproj.github.io/argo-workflows/workflow-concepts/), which provide a foundation of
understanding when working with Hera. Working through the
[Argo Walk Through](https://argoproj.github.io/argo-workflows/walk-through/) will also help you understand key concepts
before moving to Python.

## Context Managers

You will notice many classes in Hera implement the context manager interface. This was designed to mirror the YAML
syntax of Argo, helping existing users come to Hera from YAML, and for users new to both Argo and Hera, who will be able
to interpret and understand most of the existing YAML documentation and resources online from familiar naming and
functionality in Hera.

## Orchestrating Scripts

A natural extension of a Python DSL for Argo is tighter integration with Python scripts. This is where Hera improves the
developer experience through its tailored classes and syntactic sugar to enable developers to easily orchestrate Python
functions. Check out [Hello World](hello-world.md) to get started!
