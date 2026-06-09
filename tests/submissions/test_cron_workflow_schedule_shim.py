"""On-cluster test pinning the CronWorkflow.schedule -> schedules shim.

Runs in both the v4 and v3 cluster jobs. The v3 job runs *only* this file (and
any other `shim_v3_compat`-tagged tests); the v4 job runs it as part of the
full on-cluster suite. Either way, what we care about is that the payload Hera
emits for a CronWorkflow built with the legacy `schedule=` argument is
accepted by the controller.
"""

import pytest

from hera.exceptions import NotFound
from hera.workflows import Container, CronWorkflow, WorkflowsService


def _service() -> WorkflowsService:
    return WorkflowsService(
        host="https://localhost:2746",
        namespace="argo",
        verify_ssl=False,
    )


@pytest.mark.on_cluster
@pytest.mark.shim_v3_compat
def test_cron_workflow_schedule_shim_lints_on_cluster():
    """A CronWorkflow built with legacy `schedule=` must lint cleanly.

    This is the cheapest possible round-trip: lint is a server-side validation
    of the manifest, so a successful lint proves the wire payload matches the
    controller's expected schema. We use lint rather than create+delete so the
    test stays fast and idempotent.
    """
    container = Container(
        name="hello",
        image="docker/whalesay",
        command=["cowsay"],
        args=["hello from the shim"],
    )

    with pytest.warns(DeprecationWarning, match="CronWorkflowSpec.schedule was removed"):
        cw = CronWorkflow(
            name="hera-shim-cron",
            namespace="argo",
            entrypoint="hello",
            schedule="0 0 * * *",
            templates=[container],
            workflows_service=_service(),
        )

    # Sanity check: the shim cleared the legacy field and seeded schedules.
    assert cw.schedule is None
    assert cw.schedules == ["0 0 * * *"]

    # Clean up a stale fixture from a previous run, if any. Tolerated either way.
    try:
        cw.workflows_service.delete_cron_workflow(name=cw.name, namespace=cw.namespace)
    except NotFound:
        pass

    # The actual assertion: the controller accepts what we sent.
    cw.lint()
