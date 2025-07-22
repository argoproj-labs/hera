from hera.workflows import ClusterWorkflowTemplate, Container
from hera.workflows.models import Inputs, Parameter

with ClusterWorkflowTemplate(
    api_version="argoproj.io/v1alpha1",
    kind="ClusterWorkflowTemplate",
    name="cluster-workflow-template-print-message",
) as w:
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="print-message",
        args=["{{inputs.parameters.message}}"],
        command=["echo"],
        image="busybox",
    )
from hera.workflows import ClusterWorkflowTemplate, Container
from hera.workflows.models import IntOrString, RetryStrategy

with ClusterWorkflowTemplate(
    api_version="argoproj.io/v1alpha1",
    kind="ClusterWorkflowTemplate",
    name="cluster-workflow-template-random-fail-template",
) as w:
    Container(
        name="random-fail-template",
        retry_strategy=RetryStrategy(
            limit=IntOrString(
                __root__=10,
            ),
        ),
        args=["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"],
        command=["python", "-c"],
        image="python:alpine3.6",
    )
from hera.workflows import ClusterWorkflowTemplate, Container, Step, Steps
from hera.workflows.models import Arguments, Inputs, Parameter, TemplateRef

with ClusterWorkflowTemplate(
    api_version="argoproj.io/v1alpha1",
    kind="ClusterWorkflowTemplate",
    name="cluster-workflow-template-inner-steps",
) as w:
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="print-message",
        args=["{{inputs.parameters.message}}"],
        command=["echo"],
        image="busybox",
    )
    with Steps(
        name="inner-steps",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="inner-hello1",
                    )
                ],
            ),
            name="inner-hello1",
            template_ref=TemplateRef(
                cluster_scope=True,
                name="cluster-workflow-template-print-message",
                template="print-message",
            ),
        )
        with invocator.parallel():
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="inner-hello2a",
                        )
                    ],
                ),
                name="inner-hello2a",
                template_ref=TemplateRef(
                    cluster_scope=True,
                    name="cluster-workflow-template-print-message",
                    template="print-message",
                ),
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="inner-hello2b",
                        )
                    ],
                ),
                name="inner-hello2b",
                template_ref=TemplateRef(
                    cluster_scope=True,
                    name="cluster-workflow-template-print-message",
                    template="print-message",
                ),
            )
from hera.workflows import DAG, ClusterWorkflowTemplate, Container, Task
from hera.workflows.models import Arguments, Inputs, Parameter, TemplateRef

with ClusterWorkflowTemplate(
    api_version="argoproj.io/v1alpha1",
    kind="ClusterWorkflowTemplate",
    name="cluster-workflow-template-inner-dag",
) as w:
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="print-message",
        args=["{{inputs.parameters.message}}"],
        command=["echo"],
        image="busybox",
    )
    with DAG(
        name="inner-diamond",
    ) as invocator:
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="inner-A",
                    )
                ],
            ),
            name="inner-A",
            template_ref=TemplateRef(
                cluster_scope=True,
                name="cluster-workflow-template-print-message",
                template="print-message",
            ),
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="inner-B",
                    )
                ],
            ),
            name="inner-B",
            template="print-message",
            depends="inner-A",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="inner-C",
                    )
                ],
            ),
            name="inner-C",
            template="print-message",
            depends="inner-A",
        )
        Task(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="inner-D",
                    )
                ],
            ),
            name="inner-D",
            template_ref=TemplateRef(
                cluster_scope=True,
                name="cluster-workflow-template-print-message",
                template="print-message",
            ),
            depends="inner-B && inner-C",
        )
from hera.workflows import ClusterWorkflowTemplate, Container
from hera.workflows.models import Arguments, Inputs, Parameter

with ClusterWorkflowTemplate(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="message",
                value="hello world",
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="ClusterWorkflowTemplate",
    name="cluster-workflow-template-submittable",
    entrypoint="print-message",
) as w:
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="print-message",
        args=["{{inputs.parameters.message}}"],
        command=["echo"],
        image="busybox",
    )
