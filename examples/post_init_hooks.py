"""This example showcases how to register two global workflow hooks, which will modify the workflow post-init.
See `hera.global_config.WorkflowHook` for the `Protocol` specification of the hook implementation/type signature"""

from hera.workflows import GlobalConfig, Task, Workflow


# can make a custom hook that enriches the workflow by adding, for instance, labels or node selectors
def add_wf_custom_label(w: Workflow) -> None:
    w.labels = {'domain': 'testing'}


# can add custom validation rules to workflows
def check_wf_has_node_selector(w: Workflow) -> None:
    assert w.node_selector is not None


# can change the name of a task if we want to
def modify_task_name(t: Task) -> None:
    t.name = t.name + '-testing'


GlobalConfig.task_post_init_hooks = modify_task_name
GlobalConfig.workflow_post_init_hooks = add_wf_custom_label, check_wf_has_node_selector

with Workflow('w', node_selectors={"cloud.google.com/gke-accelerator": "nvidia-tesla-t4"}) as w:
    Task('t')
