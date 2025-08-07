import pytest

from hera.workflows.container import Container
from hera.workflows.container_set import ContainerSet
from hera.workflows.exceptions import InvalidTemplateCall
from hera.workflows.parameter import Parameter
from hera.workflows.workflow import Workflow


def test_container_set_callable_container_raises_error():
    with pytest.raises(InvalidTemplateCall) as e:
        # GIVEN
        with Workflow(name="w"):
            whalesay = Container(
                name="whalesay",
                inputs=[Parameter(name="message")],
                image="argoproj/argosay:v2",
                command=["cowsay"],
                args=["{{inputs.parameters.message}}"],
            )
            with ContainerSet(name="cs"):
                # WHEN
                whalesay()

    # THEN InvalidTemplateCall raised
    assert "Callable Template 'whalesay' is not under a Workflow, Steps, Parallel, or DAG context" in str(e.value)
