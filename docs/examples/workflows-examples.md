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

## Table of missing examples
| Name | Link |
|------|------|
| k8s-patch-basic | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-patch-basic.yaml |
| resubmit | https://github.com/argoproj/argo-workflows/blob/master/examples/resubmit.yaml |
| synchronization-mutex-wf-level | https://github.com/argoproj/argo-workflows/blob/master/examples/synchronization-mutex-wf-level.yaml |
| pod-metadata-wf-field | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-metadata-wf-field.yaml |
| secrets | https://github.com/argoproj/argo-workflows/blob/master/examples/secrets.yaml |
| pod-spec-patch | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-patch.yaml |
| exit-code-output-variable | https://github.com/argoproj/argo-workflows/blob/master/examples/exit-code-output-variable.yaml |
| parameter-aggregation-script | https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation-script.yaml |
| loops-sequence | https://github.com/argoproj/argo-workflows/blob/master/examples/loops-sequence.yaml |
| conditionals | https://github.com/argoproj/argo-workflows/blob/master/examples/conditionals.yaml |
| conditional-parameters | https://github.com/argoproj/argo-workflows/blob/master/examples/conditional-parameters.yaml |
| k8s-set-owner-reference | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-set-owner-reference.yaml |
| parallelism-nested-workflow | https://github.com/argoproj/argo-workflows/blob/master/examples/parallelism-nested-workflow.yaml |
| handle-large-output-results | https://github.com/argoproj/argo-workflows/blob/master/examples/handle-large-output-results.yaml |
| dag-continue-on-fail | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-continue-on-fail.yaml |
| dag-coinflip | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-coinflip.yaml |
| testvolume | https://github.com/argoproj/argo-workflows/blob/master/examples/testvolume.yaml |
| work-avoidance | https://github.com/argoproj/argo-workflows/blob/master/examples/work-avoidance.yaml |
| pod-gc-strategy | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-gc-strategy.yaml |
| pod-spec-from-previous-step | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-from-previous-step.yaml |
| global-parameters-from-configmap | https://github.com/argoproj/argo-workflows/blob/master/examples/global-parameters-from-configmap.yaml |
| dag-diamond-steps | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-diamond-steps.yaml |
| timeouts-step | https://github.com/argoproj/argo-workflows/blob/master/examples/timeouts-step.yaml |
| k8s-orchestration | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-orchestration.yaml |
| k8s-owner-reference | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-owner-reference.yaml |
| k8s-patch | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-patch.yaml |
| hello-world | https://github.com/argoproj/argo-workflows/blob/master/examples/hello-world.yaml |
| dag-conditional-artifacts | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-conditional-artifacts.yaml |
| influxdb-ci | https://github.com/argoproj/argo-workflows/blob/master/examples/influxdb-ci.yaml |
| pod-gc-strategy-with-label-selector | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-gc-strategy-with-label-selector.yaml |
| dag-daemon-task | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-daemon-task.yaml |
| workflow-template/templates | https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-template/templates.yaml |
| dag-inline-cronworkflow | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-inline-cronworkflow.yaml |
| dns-config | https://github.com/argoproj/argo-workflows/blob/master/examples/dns-config.yaml |
| pod-metadata | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-metadata.yaml |
| recursive-for-loop | https://github.com/argoproj/argo-workflows/blob/master/examples/recursive-for-loop.yaml |
| k8s-jobs | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-jobs.yaml |
| k8s-wait-wf | https://github.com/argoproj/argo-workflows/blob/master/examples/k8s-wait-wf.yaml |
| hello-hybrid | https://github.com/argoproj/argo-workflows/blob/master/examples/hello-hybrid.yaml |
| retry-with-steps | https://github.com/argoproj/argo-workflows/blob/master/examples/retry-with-steps.yaml |
| memoize-simple | https://github.com/argoproj/argo-workflows/blob/master/examples/memoize-simple.yaml |
| parameter-aggregation | https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation.yaml |
| retry-container-to-completion | https://github.com/argoproj/argo-workflows/blob/master/examples/retry-container-to-completion.yaml |
| exit-handler-dag-level | https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-dag-level.yaml |
| retry-conditional | https://github.com/argoproj/argo-workflows/blob/master/examples/retry-conditional.yaml |
| data-transformations | https://github.com/argoproj/argo-workflows/blob/master/examples/data-transformations.yaml |
| conditionals-complex | https://github.com/argoproj/argo-workflows/blob/master/examples/conditionals-complex.yaml |
| dag-inline-clusterworkflowtemplate | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-inline-clusterworkflowtemplate.yaml |
| template-defaults | https://github.com/argoproj/argo-workflows/blob/master/examples/template-defaults.yaml |
| status-reference | https://github.com/argoproj/argo-workflows/blob/master/examples/status-reference.yaml |
| expression-reusing-verbose-snippets | https://github.com/argoproj/argo-workflows/blob/master/examples/expression-reusing-verbose-snippets.yaml |
| exit-handler-slack | https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-slack.yaml |
| ci-workflowtemplate | https://github.com/argoproj/argo-workflows/blob/master/examples/ci-workflowtemplate.yaml |
| dag-disable-failFast | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-disable-failFast.yaml |
| hello-windows | https://github.com/argoproj/argo-workflows/blob/master/examples/hello-windows.yaml |
| configmaps/simple-parameters-configmap | https://github.com/argoproj/argo-workflows/blob/master/examples/configmaps/simple-parameters-configmap.yaml |
| parameter-aggregation-dag | https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation-dag.yaml |
| loops-param-argument | https://github.com/argoproj/argo-workflows/blob/master/examples/loops-param-argument.yaml |
| http-hello-world | https://github.com/argoproj/argo-workflows/blob/master/examples/http-hello-world.yaml |
| buildkit-template | https://github.com/argoproj/argo-workflows/blob/master/examples/buildkit-template.yaml |
| dag-inline-workflow | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-inline-workflow.yaml |
| map-reduce | https://github.com/argoproj/argo-workflows/blob/master/examples/map-reduce.yaml |
| resource-flags | https://github.com/argoproj/argo-workflows/blob/master/examples/resource-flags.yaml |
| gc-ttl | https://github.com/argoproj/argo-workflows/blob/master/examples/gc-ttl.yaml |
| workflow-event-binding/event-consumer-workfloweventbinding | https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-event-binding/event-consumer-workfloweventbinding.yaml |
| pod-spec-yaml-patch | https://github.com/argoproj/argo-workflows/blob/master/examples/pod-spec-yaml-patch.yaml |
| nested-workflow | https://github.com/argoproj/argo-workflows/blob/master/examples/nested-workflow.yaml |
| fun-with-gifs | https://github.com/argoproj/argo-workflows/blob/master/examples/fun-with-gifs.yaml |
| step-level-timeout | https://github.com/argoproj/argo-workflows/blob/master/examples/step-level-timeout.yaml |
| workflow-count-resourcequota | https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-count-resourcequota.yaml |
| scripts-bash | https://github.com/argoproj/argo-workflows/blob/master/examples/scripts-bash.yaml |
| daemoned-stateful-set-with-service | https://github.com/argoproj/argo-workflows/blob/master/examples/daemoned-stateful-set-with-service.yaml |
| http-success-condition | https://github.com/argoproj/argo-workflows/blob/master/examples/http-success-condition.yaml |
| retry-on-error | https://github.com/argoproj/argo-workflows/blob/master/examples/retry-on-error.yaml |
| cron-backfill | https://github.com/argoproj/argo-workflows/blob/master/examples/cron-backfill.yaml |
| scripts-python | https://github.com/argoproj/argo-workflows/blob/master/examples/scripts-python.yaml |
| dag-multiroot | https://github.com/argoproj/argo-workflows/blob/master/examples/dag-multiroot.yaml |
| daemon-step | https://github.com/argoproj/argo-workflows/blob/master/examples/daemon-step.yaml |
| fibonacci-seq-conditional-param | https://github.com/argoproj/argo-workflows/blob/master/examples/fibonacci-seq-conditional-param.yaml |
| life-cycle-hooks-tmpl-level | https://github.com/argoproj/argo-workflows/blob/master/examples/life-cycle-hooks-tmpl-level.yaml |
| artifacts-workflowtemplate | https://github.com/argoproj/argo-workflows/blob/master/examples/artifacts-workflowtemplate.yaml |
| scripts-javascript | https://github.com/argoproj/argo-workflows/blob/master/examples/scripts-javascript.yaml |
| ci | https://github.com/argoproj/argo-workflows/blob/master/examples/ci.yaml |
| global-outputs | https://github.com/argoproj/argo-workflows/blob/master/examples/global-outputs.yaml |
| cluster-workflow-template/clustertemplates | https://github.com/argoproj/argo-workflows/blob/master/examples/cluster-workflow-template/clustertemplates.yaml |
| exit-handlers | https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handlers.yaml |
| expression-tag-template-workflow | https://github.com/argoproj/argo-workflows/blob/master/examples/expression-tag-template-workflow.yaml |
| expression-destructure-json | https://github.com/argoproj/argo-workflows/blob/master/examples/expression-destructure-json.yaml |
| label-value-from-workflow | https://github.com/argoproj/argo-workflows/blob/master/examples/label-value-from-workflow.yaml |
| exit-handler-with-param | https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-with-param.yaml |
