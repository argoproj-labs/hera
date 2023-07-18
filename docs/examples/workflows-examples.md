# Workflows Examples

Hera has complete feature parity with YAML as a definition language for Argo Workflows. To demonstrate the equivalency
(and improvements that Hera offers), we provide two collections of examples.

The "Upstream" collection contains examples
[directly from the Argo Workflows repository](https://github.com/argoproj/argo-workflows/tree/6e97c7d/examples), such as
the [DAG Diamond example](workflows/upstream/dag_diamond.md), to demonstrate how the YAML spec maps to Hera classes.
These examples are generated and compared in Hera's CI/CD pipeline to ensure that all the examples are possible to
recreate in Hera.

> If you'd like to contribute missing examples, please see the table below and follow the
> [Contributing Guide](/CONTRIBUTING.md)!

The "Hera" collection shows off features and idiomatic usage of Hera such as the
[Coinflip example](workflows/coinflip.md) using the script decorator.

## List of missing examples
| Example |
|---------|
| [pod-gc-strategy](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-gc-strategy.yaml) |
| [global-parameters-from-configmap](https://github.com/argoproj/argo-workflows/blob/master/examples/global-parameters-from-configmap.yaml) |
| [k8s-jobs](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-jobs.yaml) |
| [data-transformations](https://github.com/argoproj/argo-workflows/blob/master/examples/data-transformations.yaml) |
| [hello-windows](https://github.com/argoproj/argo-workflows/blob/master/examples/hello-windows.yaml) |
| [scripts-javascript](https://github.com/argoproj/argo-workflows/blob/master/examples/scripts-javascript.yaml) |
| [fun-with-gifs](https://github.com/argoproj/argo-workflows/blob/master/examples/fun-with-gifs.yaml) |
| [k8s-wait-wf](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-wait-wf.yaml) |
| [cron-backfill](https://github.com/argoproj/argo-workflows/blob/master/examples/cron-backfill.yaml) |
| [template-defaults](https://github.com/argoproj/argo-workflows/blob/master/examples/template-defaults.yaml) |
| [testvolume](https://github.com/argoproj/argo-workflows/blob/master/examples/testvolume.yaml) |
| [hello-world](https://github.com/argoproj/argo-workflows/blob/master/examples/hello-world.yaml) |
| [http-hello-world](https://github.com/argoproj/argo-workflows/blob/master/examples/http-hello-world.yaml) |
| [status-reference](https://github.com/argoproj/argo-workflows/blob/master/examples/status-reference.yaml) |
| [life-cycle-hooks-tmpl-level](https://github.com/argoproj/argo-workflows/blob/master/examples/life-cycle-hooks-tmpl-level.yaml) |
| [dag-daemon-task](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-daemon-task.yaml) |
| [influxdb-ci](https://github.com/argoproj/argo-workflows/blob/master/examples/influxdb-ci.yaml) |
| [retry-container-to-completion](https://github.com/argoproj/argo-workflows/blob/master/examples/retry-container-to-completion.yaml) |
| [exit-handlers](https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handlers.yaml) |
| [loops-sequence](https://github.com/argoproj/argo-workflows/blob/master/examples/loops-sequence.yaml) |
| [global-outputs](https://github.com/argoproj/argo-workflows/blob/master/examples/global-outputs.yaml) |
| [resubmit](https://github.com/argoproj/argo-workflows/blob/master/examples/resubmit.yaml) |
| [retry-with-steps](https://github.com/argoproj/argo-workflows/blob/master/examples/retry-with-steps.yaml) |
| [daemoned-stateful-set-with-service](https://github.com/argoproj/argo-workflows/blob/master/examples/daemoned-stateful-set-with-service.yaml) |
| [handle-large-output-results](https://github.com/argoproj/argo-workflows/blob/master/examples/handle-large-output-results.yaml) |
| [configmaps/simple-parameters-configmap](https://github.com/argoproj/argo-workflows/blob/master/examples/configmaps/simple-parameters-configmap.yaml) |
| [artifacts-workflowtemplate](https://github.com/argoproj/argo-workflows/blob/master/examples/artifacts-workflowtemplate.yaml) |
| [pod-metadata](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-metadata.yaml) |
| [http-success-condition](https://github.com/argoproj/argo-workflows/blob/master/examples/http-success-condition.yaml) |
| [pod-metadata-wf-field](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-metadata-wf-field.yaml) |
| [expression-reusing-verbose-snippets](https://github.com/argoproj/argo-workflows/blob/master/examples/expression-reusing-verbose-snippets.yaml) |
| [conditional-parameters](https://github.com/argoproj/argo-workflows/blob/master/examples/conditional-parameters.yaml) |
| [label-value-from-workflow](https://github.com/argoproj/argo-workflows/blob/master/examples/label-value-from-workflow.yaml) |
| [dag-inline-workflow](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-inline-workflow.yaml) |
| [parallelism-nested-workflow](https://github.com/argoproj/argo-workflows/blob/master/examples/parallelism-nested-workflow.yaml) |
| [workflow-event-binding/event-consumer-workfloweventbinding](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-event-binding/event-consumer-workfloweventbinding.yaml) |
| [dag-inline-cronworkflow](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-inline-cronworkflow.yaml) |
| [parameter-aggregation-dag](https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation-dag.yaml) |
| [step-level-timeout](https://github.com/argoproj/argo-workflows/blob/master/examples/step-level-timeout.yaml) |
| [retry-conditional](https://github.com/argoproj/argo-workflows/blob/master/examples/retry-conditional.yaml) |
| [scripts-python](https://github.com/argoproj/argo-workflows/blob/master/examples/scripts-python.yaml) |
| [memoize-simple](https://github.com/argoproj/argo-workflows/blob/master/examples/memoize-simple.yaml) |
| [ci-workflowtemplate](https://github.com/argoproj/argo-workflows/blob/master/examples/ci-workflowtemplate.yaml) |
| [secrets](https://github.com/argoproj/argo-workflows/blob/master/examples/secrets.yaml) |
| [k8s-orchestration](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-orchestration.yaml) |
| [exit-code-output-variable](https://github.com/argoproj/argo-workflows/blob/master/examples/exit-code-output-variable.yaml) |
| [buildkit-template](https://github.com/argoproj/argo-workflows/blob/master/examples/buildkit-template.yaml) |
| [cluster-workflow-template/clustertemplates](https://github.com/argoproj/argo-workflows/blob/master/examples/cluster-workflow-template/clustertemplates.yaml) |
| [retry-on-error](https://github.com/argoproj/argo-workflows/blob/master/examples/retry-on-error.yaml) |
| [exit-handler-dag-level](https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-dag-level.yaml) |
| [dag-continue-on-fail](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-continue-on-fail.yaml) |
| [pod-spec-from-previous-step](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-from-previous-step.yaml) |
| [pod-spec-yaml-patch](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-yaml-patch.yaml) |
| [expression-tag-template-workflow](https://github.com/argoproj/argo-workflows/blob/master/examples/expression-tag-template-workflow.yaml) |
| [fibonacci-seq-conditional-param](https://github.com/argoproj/argo-workflows/blob/master/examples/fibonacci-seq-conditional-param.yaml) |
| [parameter-aggregation](https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation.yaml) |
| [expression-destructure-json](https://github.com/argoproj/argo-workflows/blob/master/examples/expression-destructure-json.yaml) |
| [workflow-count-resourcequota](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-count-resourcequota.yaml) |
| [k8s-set-owner-reference](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-set-owner-reference.yaml) |
| [dag-diamond-steps](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-diamond-steps.yaml) |
| [gc-ttl](https://github.com/argoproj/argo-workflows/blob/master/examples/gc-ttl.yaml) |
| [k8s-patch](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-patch.yaml) |
| [dag-coinflip](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-coinflip.yaml) |
| [dag-conditional-artifacts](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-conditional-artifacts.yaml) |
| [k8s-patch-basic](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-patch-basic.yaml) |
| [resource-flags](https://github.com/argoproj/argo-workflows/blob/master/examples/resource-flags.yaml) |
| [dag-disable-failFast](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-disable-failFast.yaml) |
| [timeouts-step](https://github.com/argoproj/argo-workflows/blob/master/examples/timeouts-step.yaml) |
| [scripts-bash](https://github.com/argoproj/argo-workflows/blob/master/examples/scripts-bash.yaml) |
| [pod-spec-patch](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-patch.yaml) |
| [hello-hybrid](https://github.com/argoproj/argo-workflows/blob/master/examples/hello-hybrid.yaml) |
| [workflow-template/templates](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-template/templates.yaml) |
| [exit-handler-with-param](https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-with-param.yaml) |
| [daemon-step](https://github.com/argoproj/argo-workflows/blob/master/examples/daemon-step.yaml) |
| [parameter-aggregation-script](https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation-script.yaml) |
| [k8s-owner-reference](https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-owner-reference.yaml) |
| [loops-param-argument](https://github.com/argoproj/argo-workflows/blob/master/examples/loops-param-argument.yaml) |
| [conditionals](https://github.com/argoproj/argo-workflows/blob/master/examples/conditionals.yaml) |
| [map-reduce](https://github.com/argoproj/argo-workflows/blob/master/examples/map-reduce.yaml) |
| [ci](https://github.com/argoproj/argo-workflows/blob/master/examples/ci.yaml) |
| [dag-inline-clusterworkflowtemplate](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-inline-clusterworkflowtemplate.yaml) |
| [nested-workflow](https://github.com/argoproj/argo-workflows/blob/master/examples/nested-workflow.yaml) |
| [synchronization-mutex-wf-level](https://github.com/argoproj/argo-workflows/blob/master/examples/synchronization-mutex-wf-level.yaml) |
| [dns-config](https://github.com/argoproj/argo-workflows/blob/master/examples/dns-config.yaml) |
| [dag-multiroot](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-multiroot.yaml) |
| [work-avoidance](https://github.com/argoproj/argo-workflows/blob/master/examples/work-avoidance.yaml) |
| [exit-handler-slack](https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-slack.yaml) |
| [recursive-for-loop](https://github.com/argoproj/argo-workflows/blob/master/examples/recursive-for-loop.yaml) |
| [conditionals-complex](https://github.com/argoproj/argo-workflows/blob/master/examples/conditionals-complex.yaml) |
| [pod-gc-strategy-with-label-selector](https://github.com/argoproj/argo-workflows/blob/master/examples/pod-gc-strategy-with-label-selector.yaml) |
