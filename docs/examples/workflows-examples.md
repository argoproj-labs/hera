# Workflows Examples

Hera has complete feature parity with YAML as a definition language for Argo Workflows.

The examples show off features and idiomatic usage of Hera such as the
[Coinflip example](workflows/scripts/coinflip.md) recreated using the script decorator.

The "Upstream" collection contains examples
[directly from the Argo Workflows repository](https://github.com/argoproj/argo-workflows/tree/6e97c7d/examples), such as
the [DAG Diamond example](workflows/upstream/dag_diamond.md), to demonstrate how the YAML spec maps to Hera classes.
They may not be written as idiomatic Hera code (for example, using `Container` when a script decorator would be
preferred).

> If you'd like to contribute missing examples, please see the table below and follow the
> [Contributing Guide](../CONTRIBUTING.md)!

Explore the examples through the side bar!

## List of **missing** examples

*You can help by contributing these examples!*

| Example |
|---------|
| [cluster-workflow-template/clustertemplates](https://github.com/argoproj/argo-workflows/blob/main/examples/cluster-workflow-template/clustertemplates.yaml) |
| [configmaps/simple-parameters-configmap](https://github.com/argoproj/argo-workflows/blob/main/examples/configmaps/simple-parameters-configmap.yaml) |
| [cron-backfill](https://github.com/argoproj/argo-workflows/blob/main/examples/cron-backfill.yaml) |
| [dag-disable-failFast](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-disable-failFast.yaml) |
| [dag-inline-clusterworkflowtemplate](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-clusterworkflowtemplate.yaml) |
| [dag-inline-cronworkflow](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-cronworkflow.yaml) |
| [dag-inline-workflow](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-workflow.yaml) |
| [data-transformations](https://github.com/argoproj/argo-workflows/blob/main/examples/data-transformations.yaml) |
| [expression-destructure-json](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-destructure-json.yaml) |
| [expression-destructure-json-complex](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-destructure-json-complex.yaml) |
| [expression-reusing-verbose-snippets](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-reusing-verbose-snippets.yaml) |
| [fibonacci-seq-conditional-param](https://github.com/argoproj/argo-workflows/blob/main/examples/fibonacci-seq-conditional-param.yaml) |
| [memoize-simple](https://github.com/argoproj/argo-workflows/blob/main/examples/memoize-simple.yaml) |
| [parameter-aggregation](https://github.com/argoproj/argo-workflows/blob/main/examples/parameter-aggregation.yaml) |
| [parameter-aggregation-script](https://github.com/argoproj/argo-workflows/blob/main/examples/parameter-aggregation-script.yaml) |
| [pod-spec-from-previous-step](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-from-previous-step.yaml) |
| [scripts-bash](https://github.com/argoproj/argo-workflows/blob/main/examples/scripts-bash.yaml) |
| [scripts-javascript](https://github.com/argoproj/argo-workflows/blob/main/examples/scripts-javascript.yaml) |
| [testvolume](https://github.com/argoproj/argo-workflows/blob/main/examples/testvolume.yaml) |
| [work-avoidance](https://github.com/argoproj/argo-workflows/blob/main/examples/work-avoidance.yaml) |
| [workflow-count-resourcequota](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-count-resourcequota.yaml) |
| [workflow-event-binding/event-consumer-workfloweventbinding](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-event-binding/event-consumer-workfloweventbinding.yaml) |
| [workflow-event-binding/github-path-filter-workfloweventbinding](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-event-binding/github-path-filter-workfloweventbinding.yaml) |
| [workflow-event-binding/github-path-filter-workflowtemplate](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-event-binding/github-path-filter-workflowtemplate.yaml) |
| [workflow-template/templates](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-template/templates.yaml) |
