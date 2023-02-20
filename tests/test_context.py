from hera.workflows._context import _DAG_context
from hera.workflows.dag import DAG
from hera.workflows.task import Task


class TestDAGContext:
    def test_enter_appends_dag(self):
        ctx = _DAG_context()
        ctx.enter(DAG("d"))
        assert len(ctx._dags) == 1
        assert ctx._dags[0].name == "d"

    def test_exit_pops_dag(self):
        ctx = _DAG_context()
        ctx.enter(DAG("d"))
        ctx.exit()
        assert len(ctx._dags) == 0

    def test_is_set_returns_expected_value(self):
        ctx = _DAG_context()
        ctx.enter(DAG("d"))
        assert ctx.is_set()
        ctx.exit()
        assert not ctx.is_set()

    def test_add_task_adds_expected_task(self):
        ctx = _DAG_context()
        ctx.enter(DAG("d"))
        assert len(ctx._dags) == 1
        ctx.add_task(Task("a"))
        assert len(ctx._dags[0].tasks) == 1
        assert ctx._dags[0].tasks[0].name == "a"

    def test_add_tasks_adds_expected_tasks(self):
        ctx = _DAG_context()
        ctx.enter(DAG("a"))
        ctx.enter(DAG("b"))
        assert len(ctx._dags) == 2
        ctx.add_tasks(Task("a"), Task("b"))
        assert len(ctx._dags[0].tasks) == 0
        assert len(ctx._dags[-1].tasks) == 2
        assert ctx._dags[-1].tasks[0].name == "a"
        assert ctx._dags[-1].tasks[1].name == "b"
