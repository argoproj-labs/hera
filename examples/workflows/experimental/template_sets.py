from hera.shared import global_config
from hera.workflows import Output, TemplateSet, Workflow

global_config.experimental_features["decorator_syntax"] = True

w = Workflow(name="my-workflow")
templates = TemplateSet()


@templates.script()
def setup() -> Output:
    return Output(result="Setting things up")


@templates.dag()
def my_dag():
    setup(name="task-a")
    setup(name="task-b")


w.add_template_set(templates)
