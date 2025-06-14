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
| [artifacts-workflowtemplate](https://github.com/argoproj/argo-workflows/blob/main/examples/artifacts-workflowtemplate.yaml) |
| [buildkit-template](https://github.com/argoproj/argo-workflows/blob/main/examples/buildkit-template.yaml) |
| [ci](https://github.com/argoproj/argo-workflows/blob/main/examples/ci.yaml) |
| [cluster-workflow-template/clustertemplates](https://github.com/argoproj/argo-workflows/blob/main/examples/cluster-workflow-template/clustertemplates.yaml) |
| [conditional-parameters](https://github.com/argoproj/argo-workflows/blob/main/examples/conditional-parameters.yaml) |
| [conditionals](https://github.com/argoproj/argo-workflows/blob/main/examples/conditionals.yaml) |
| [conditionals-complex](https://github.com/argoproj/argo-workflows/blob/main/examples/conditionals-complex.yaml) |
| [configmaps/simple-parameters-configmap](https://github.com/argoproj/argo-workflows/blob/main/examples/configmaps/simple-parameters-configmap.yaml) |
| [cron-backfill](https://github.com/argoproj/argo-workflows/blob/main/examples/cron-backfill.yaml) |
| [daemon-step](https://github.com/argoproj/argo-workflows/blob/main/examples/daemon-step.yaml) |
| [daemoned-stateful-set-with-service](https://github.com/argoproj/argo-workflows/blob/main/examples/daemoned-stateful-set-with-service.yaml) |
| [dag-coinflip](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-coinflip.yaml) |
| [dag-conditional-artifacts](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-conditional-artifacts.yaml) |
| [dag-continue-on-fail](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-continue-on-fail.yaml) |
| [dag-daemon-retry-strategy](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-daemon-retry-strategy.yaml) |
| [dag-daemon-task](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-daemon-task.yaml) |
| [dag-diamond-steps](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-diamond-steps.yaml) |
| [dag-disable-failFast](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-disable-failFast.yaml) |
| [dag-inline-clusterworkflowtemplate](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-clusterworkflowtemplate.yaml) |
| [dag-inline-cronworkflow](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-cronworkflow.yaml) |
| [dag-inline-workflow](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-workflow.yaml) |
| [dag-multiroot](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-multiroot.yaml) |
| [data-transformations](https://github.com/argoproj/argo-workflows/blob/main/examples/data-transformations.yaml) |
| [dns-config](https://github.com/argoproj/argo-workflows/blob/main/examples/dns-config.yaml) |
| [exit-code-output-variable](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-code-output-variable.yaml) |
| [exit-handler-dag-level](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-dag-level.yaml) |
| [exit-handler-slack](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-slack.yaml) |
| [exit-handler-with-param](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handler-with-param.yaml) |
| [exit-handlers](https://github.com/argoproj/argo-workflows/blob/main/examples/exit-handlers.yaml) |
| [expression-destructure-json](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-destructure-json.yaml) |
| [expression-destructure-json-complex](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-destructure-json-complex.yaml) |
| [expression-reusing-verbose-snippets](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-reusing-verbose-snippets.yaml) |
| [expression-tag-template-workflow](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-tag-template-workflow.yaml) |
| [fibonacci-seq-conditional-param](https://github.com/argoproj/argo-workflows/blob/main/examples/fibonacci-seq-conditional-param.yaml) |
| [fun-with-gifs](https://github.com/argoproj/argo-workflows/blob/main/examples/fun-with-gifs.yaml) |
| [gc-ttl](https://github.com/argoproj/argo-workflows/blob/main/examples/gc-ttl.yaml) |
| [global-outputs](https://github.com/argoproj/argo-workflows/blob/main/examples/global-outputs.yaml) |
| [global-parameters-from-configmap](https://github.com/argoproj/argo-workflows/blob/main/examples/global-parameters-from-configmap.yaml) |
| [handle-large-output-results](https://github.com/argoproj/argo-workflows/blob/main/examples/handle-large-output-results.yaml) |
| [hello-hybrid](https://github.com/argoproj/argo-workflows/blob/main/examples/hello-hybrid.yaml) |
| [hello-windows](https://github.com/argoproj/argo-workflows/blob/main/examples/hello-windows.yaml) |
| [hello-world](https://github.com/argoproj/argo-workflows/blob/main/examples/hello-world.yaml) |
| [http-hello-world](https://github.com/argoproj/argo-workflows/blob/main/examples/http-hello-world.yaml) |
| [http-success-condition](https://github.com/argoproj/argo-workflows/blob/main/examples/http-success-condition.yaml) |
| [influxdb-ci](https://github.com/argoproj/argo-workflows/blob/main/examples/influxdb-ci.yaml) |
| [intermediate-parameters](https://github.com/argoproj/argo-workflows/blob/main/examples/intermediate-parameters.yaml) |
| [k8s-jobs](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-jobs.yaml) |
| [k8s-orchestration](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-orchestration.yaml) |
| [k8s-owner-reference](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-owner-reference.yaml) |
| [k8s-patch-json-pod](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-json-pod.yaml) |
| [k8s-patch-merge-pod](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-merge-pod.yaml) |
| [k8s-patch-pod](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-patch-pod.yaml) |
| [k8s-wait-wf](https://github.com/argoproj/argo-workflows/blob/main/examples/k8s-wait-wf.yaml) |
| [label-value-from-workflow](https://github.com/argoproj/argo-workflows/blob/main/examples/label-value-from-workflow.yaml) |
| [loops-param-argument](https://github.com/argoproj/argo-workflows/blob/main/examples/loops-param-argument.yaml) |
| [loops-sequence](https://github.com/argoproj/argo-workflows/blob/main/examples/loops-sequence.yaml) |
| [map-reduce](https://github.com/argoproj/argo-workflows/blob/main/examples/map-reduce.yaml) |
| [memoize-simple](https://github.com/argoproj/argo-workflows/blob/main/examples/memoize-simple.yaml) |
| [nested-workflow](https://github.com/argoproj/argo-workflows/blob/main/examples/nested-workflow.yaml) |
| [parallelism-nested-workflow](https://github.com/argoproj/argo-workflows/blob/main/examples/parallelism-nested-workflow.yaml) |
| [parameter-aggregation](https://github.com/argoproj/argo-workflows/blob/main/examples/parameter-aggregation.yaml) |
| [parameter-aggregation-dag](https://github.com/argoproj/argo-workflows/blob/main/examples/parameter-aggregation-dag.yaml) |
| [parameter-aggregation-script](https://github.com/argoproj/argo-workflows/blob/main/examples/parameter-aggregation-script.yaml) |
| [pod-gc-strategy](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-gc-strategy.yaml) |
| [pod-gc-strategy-with-label-selector](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-gc-strategy-with-label-selector.yaml) |
| [pod-metadata](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-metadata.yaml) |
| [pod-metadata-wf-field](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-metadata-wf-field.yaml) |
| [pod-spec-from-previous-step](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-from-previous-step.yaml) |
| [pod-spec-patch](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-patch.yaml) |
| [pod-spec-yaml-patch](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-spec-yaml-patch.yaml) |
| [recursive-for-loop](https://github.com/argoproj/argo-workflows/blob/main/examples/recursive-for-loop.yaml) |
| [resource-flags](https://github.com/argoproj/argo-workflows/blob/main/examples/resource-flags.yaml) |
| [resubmit](https://github.com/argoproj/argo-workflows/blob/main/examples/resubmit.yaml) |
| [retry-conditional](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-conditional.yaml) |
| [retry-container-to-completion](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-container-to-completion.yaml) |
| [retry-on-error](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-on-error.yaml) |
| [retry-with-steps](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-with-steps.yaml) |
| [scripts-bash](https://github.com/argoproj/argo-workflows/blob/main/examples/scripts-bash.yaml) |
| [scripts-javascript](https://github.com/argoproj/argo-workflows/blob/main/examples/scripts-javascript.yaml) |
| [secrets](https://github.com/argoproj/argo-workflows/blob/main/examples/secrets.yaml) |
| [status-reference](https://github.com/argoproj/argo-workflows/blob/main/examples/status-reference.yaml) |
| [step-level-timeout](https://github.com/argoproj/argo-workflows/blob/main/examples/step-level-timeout.yaml) |
| [steps-daemon-retry-strategy](https://github.com/argoproj/argo-workflows/blob/main/examples/steps-daemon-retry-strategy.yaml) |
| [synchronization-db-mutex-tmpl-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-db-mutex-tmpl-level.yaml) |
| [synchronization-db-mutex-wf-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-db-mutex-wf-level.yaml) |
| [synchronization-db-tmpl-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-db-tmpl-level.yaml) |
| [synchronization-db-wf-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-db-wf-level.yaml) |
| [synchronization-mutex-tmpl-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-mutex-tmpl-level.yaml) |
| [synchronization-mutex-wf-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-mutex-wf-level.yaml) |
| [synchronization-mutex-wf-level-legacy](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-mutex-wf-level-legacy.yaml) |
| [synchronization-tmpl-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-tmpl-level.yaml) |
| [synchronization-wf-level](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-wf-level.yaml) |
| [template-defaults](https://github.com/argoproj/argo-workflows/blob/main/examples/template-defaults.yaml) |
| [testvolume](https://github.com/argoproj/argo-workflows/blob/main/examples/testvolume.yaml) |
| [timeouts-step](https://github.com/argoproj/argo-workflows/blob/main/examples/timeouts-step.yaml) |
| [title-and-description-with-markdown](https://github.com/argoproj/argo-workflows/blob/main/examples/title-and-description-with-markdown.yaml) |
| [withsequence-nested-result](https://github.com/argoproj/argo-workflows/blob/main/examples/withsequence-nested-result.yaml) |
| [work-avoidance](https://github.com/argoproj/argo-workflows/blob/main/examples/work-avoidance.yaml) |
| [workflow-count-resourcequota](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-count-resourcequota.yaml) |
| [workflow-event-binding/event-consumer-workfloweventbinding](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-event-binding/event-consumer-workfloweventbinding.yaml) |
| [workflow-event-binding/github-path-filter-workfloweventbinding](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-event-binding/github-path-filter-workfloweventbinding.yaml) |
| [workflow-event-binding/github-path-filter-workflowtemplate](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-event-binding/github-path-filter-workflowtemplate.yaml) |
| [workflow-template/templates](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-template/templates.yaml) |
