# About Hera

Hera is a Python library that allows you to construct and submit Argo Workflows. **Anything you can write in YAML for
Argo Workflows you can express in Hera!** It is designed to be intuitive and easy to use, while also providing a
powerful interface to the underlying Argo API.

If you are a new user of Argo, we encourage you to become familiar with
[Argo's Core Concepts](https://argoproj.github.io/argo-workflows/workflow-concepts/), which provide a foundation of
understanding when working with Hera. Working through the
[Argo Walkthrough](https://argoproj.github.io/argo-workflows/walk-through/) will also help you understand key concepts
before moving to Python.

## Feature Parity

Hera offers hand-written custom classes with features to make Workflow-authoring easier, but also includes
auto-generated classes from the Argo Workflows OpenAPI specification as a backup, which integrate with the custom
classes. This allows you to, as mentioned above, write everything in Hera, without the use of YAML.

You can check out the extensive ["upstream" examples](../examples/workflows/upstream/dag_diamond.md) that contain
side-by-side Python and YAML definitions for Workflows in
[the Argo examples folder on GitHub](https://github.com/argoproj/argo-workflows/tree/master/examples).

## Hera Roadmap

We ran the first Developer Survey in 2025,
[read the results blog here](https://dev.to/elliot_gunton/hera-developer-survey-2025-168d). The results of the Developer
Survey helped to inform the items on the Hera Roadmap –
[read through the Roadmap here](https://docs.google.com/document/d/1A9HIESzPTHldvh4nkBE4F45p337_88Z3i66FN-48OfU/edit?usp=sharing)!
