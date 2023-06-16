# Workflows Examples

Hera has complete feature parity with YAML as a definition language for Argo Workflows. To demonstrate the equivalency
(and improvements that Hera offers), we provide two collections of examples.

The "Upstream" collection contains examples
[directly from the Argo Workflows repository](https://github.com/argoproj/argo-workflows/tree/6e97c7d/examples), such as
the [DAG Diamond example](workflows/upstream/dag_diamond.md), to demonstrate how the YAML spec maps to Hera classes.
These examples are generated and compared in Hera's CI/CD pipeline to ensure that all the examples are possible to
recreate in Hera.

The "Hera" collection shows off features and idiomatic usage of Hera such as the
[Coinflip example](workflows/coinflip.md) using the script decorator.
