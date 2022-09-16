import json

import pytest
from argo_workflows.model.capabilities import Capabilities
from argo_workflows.model.security_context import SecurityContext
from argo_workflows.models import IoArgoprojWorkflowV1alpha1Inputs
from argo_workflows.models import Toleration as _ArgoToleration

from hera import (
    ConfigMapEnvFromSpec,
    ConfigMapEnvSpec,
    ConfigMapVolume,
    EmptyDirVolume,
    EnvSpec,
    ExistingVolume,
    GCSArtifact,
    GitArtifact,
    GPUToleration,
    Memoize,
    Operator,
    Parameter,
    Resources,
    ResourceTemplate,
    Retry,
    RetryPolicy,
    S3Artifact,
    Task,
    TaskResult,
    TaskSecurityContext,
    TemplateRef,
    Toleration,
    Volume,
    WorkflowStatus,
)


def test_next_and_shifting_set_correct_dependencies(no_op):
    t1, t2, t3 = Task("t1", no_op), Task("t2", no_op), Task("t3", no_op)
    t1.next(t2).next(t3)
    assert t2.depends == "t1"
    assert t3.depends == "t2"

    t4, t5, t6 = Task("t4", no_op), Task("t5", no_op), Task("t6", no_op)
    t4 >> t5 >> t6
    assert t5.depends == "t4"
    assert t6.depends == "t5"


def test_next_does_not_set_dependency_multiple_times():
    t1, t2 = Task("t1"), Task("t2")
    t1 >> t2
    assert t2.depends == "t1"
    with pytest.raises(ValueError):
        # Already added
        t1 >> t2


def test_retry_limits_fail_validation():
    with pytest.raises(AssertionError):
        Retry(duration=5, max_duration=4)


def test_func_and_func_param_validation_raises_on_args_not_passed(op):
    with pytest.raises(ValueError) as e:
        Task("t", op, [])
    assert (
        str(e.value)
        == "`with_params` is empty and there exists non-default arguments which aren't covered by `inputs`: {'a'}"
    )


def test_func_and_func_param_validation_raises_on_difference(op):
    with pytest.raises(ValueError) as e:
        Task("t", op, [{"a": 1}, {"b": 1}])
    assert str(e.value) == "param in `with_params` misses non-default argument: {'a'}"


def test_param_getter_returns_empty(no_op):
    t = Task("t", no_op)
    assert not t.inputs


def test_param_getter_parses_on_multi_params(op):
    t = Task("t", op, [{"a": 1}, {"a": 2}, {"a": 3}])
    for i in t.inputs:
        assert isinstance(i, Parameter)
        assert i.name == "a"
        assert i.value == "{{item.a}}"


def test_param_getter_parses_single_param_val_on_json_payload(op):
    t = Task("t", op, [{"a": 1}])
    assert len(t.inputs) == 1
    first_input = t.inputs[0]
    assert isinstance(first_input, Parameter)
    assert first_input.name == "a"
    assert first_input.value == "{{item.a}}"


def test_param_script_portion_adds_formatted_json_calls(op):
    t = Task("t", op, [{"a": 1}])
    script = t._get_param_script_portion()
    assert (
        script == "import json\n"
        "try: a = json.loads('''{{inputs.parameters.a}}''')\n"
        "except: a = '''{{inputs.parameters.a}}'''\n"
    )


def test_script_getter_returns_expected_string(op, typed_op):
    t = Task("t", op, [{"a": 1}])
    script = t._get_script()
    assert (
        script == "import os\nimport sys\nsys.path.append(os.getcwd())\n"
        "import json\n"
        "try: a = json.loads('''{{inputs.parameters.a}}''')\n"
        "except: a = '''{{inputs.parameters.a}}'''\n"
        "\n"
        "print(a)\n"
    )

    t = Task("t", typed_op, [{"a": 1}])
    script = t._get_script()
    assert (
        script == "import os\nimport sys\nsys.path.append(os.getcwd())\n"
        "import json\n"
        "try: a = json.loads('''{{inputs.parameters.a}}''')\n"
        "except: a = '''{{inputs.parameters.a}}'''\n"
        "\n"
        "print(a)\n"
        'return [{"a": (a, a)}]\n'
    )


# def test_script_non_python():
#     pass


def test_script_getter_parses_multi_line_function(long_op):
    t = Task(
        "t",
        long_op,
        [
            {
                "very_long_parameter_name": 1,
                "very_very_long_parameter_name": 2,
                "very_very_very_long_parameter_name": 3,
                "very_very_very_very_long_parameter_name": 4,
                "very_very_very_very_very_long_parameter_name": 5,
            }
        ],
    )

    expected_script = """import os
import sys
sys.path.append(os.getcwd())
import json
try: very_long_parameter_name = json.loads('''{{inputs.parameters.very_long_parameter_name}}''')
except: very_long_parameter_name = '''{{inputs.parameters.very_long_parameter_name}}'''
try: very_very_long_parameter_name = json.loads('''{{inputs.parameters.very_very_long_parameter_name}}''')
except: very_very_long_parameter_name = '''{{inputs.parameters.very_very_long_parameter_name}}'''
try: very_very_very_long_parameter_name = json.loads('''{{inputs.parameters.very_very_very_long_parameter_name}}''')
except: very_very_very_long_parameter_name = '''{{inputs.parameters.very_very_very_long_parameter_name}}'''
try: very_very_very_very_long_parameter_name = json.loads('''{{inputs.parameters.very_very_very_very_long_parameter_name}}''')
except: very_very_very_very_long_parameter_name = '''{{inputs.parameters.very_very_very_very_long_parameter_name}}'''
try: very_very_very_very_very_long_parameter_name = json.loads('''{{inputs.parameters.very_very_very_very_very_long_parameter_name}}''')
except: very_very_very_very_very_long_parameter_name = '''{{inputs.parameters.very_very_very_very_very_long_parameter_name}}'''

print(42)
"""
    assert t._get_script() == expected_script


def test_resources_returned_with_appropriate_limits(op):
    r = Resources(cpu_request=1, memory_request="4Gi")
    t = Task("t", op, [{"a": 1}], resources=r)
    resources = t._build_script().resources

    assert resources["request"]["cpu"] == "1"
    assert resources["request"]["memory"] == "4Gi"


def test_resources_returned_with_gpus(op):
    r = Resources(gpus=2)
    t = Task("t", op, [{"a": 1}], resources=r)
    resources = t._build_script().resources

    assert resources["request"]["nvidia.com/gpu"] == "2"
    assert resources["limit"]["nvidia.com/gpu"] == "2"


def test_volume_mounts_returns_expected_volumes(no_op):
    t = Task(
        "t",
        no_op,
        volumes=[
            Volume(name="v1", size="1Gi", mount_path="/v1"),
            ExistingVolume(name="v2", mount_path="/v2"),
            EmptyDirVolume(name="v3"),
            ConfigMapVolume(config_map_name="cfm", mount_path="/v3"),
        ],
    )
    vs = t._build_volume_mounts()
    assert vs[0].name == "v1"
    assert vs[0].mount_path == "/v1"
    assert vs[1].name == "v2"
    assert vs[1].mount_path == "/v2"
    assert vs[2].name == "v3"
    assert vs[2].mount_path == "/dev/shm"
    assert vs[3].name
    assert vs[3].mount_path == "/v3"


def test_gpu_toleration_returns_expected_toleration():
    tn = GPUToleration
    assert tn.key == "nvidia.com/gpu"
    assert tn.effect == "NoSchedule"
    assert tn.operator == "Equal"
    assert tn.value == "present"


def test_task_with_default_value_in_toleration(no_op):
    toleration = Toleration(key="nvidia.com/gpu", effect="NoSchedule", operator="Equal")
    t = Task("t", no_op, tolerations=[toleration])

    assert t.tolerations[0].value == ""
    assert t.tolerations[0].key == "nvidia.com/gpu"
    assert t.tolerations[0].effect == "NoSchedule"
    assert t.tolerations[0].operator == "Equal"


def test_task_command_parses(op):
    t = Task("t", op, with_param=[{"a": 1}])
    assert t.get_command() == ["python"]


def test_task_spec_returns_with_param(op):
    items = [{"a": 1}, {"a": 1}, {"a": 1}]
    t = Task("t", op, with_param=items)
    s = t._build_dag_task()

    assert s.name == "t"
    assert s.template == "t"
    assert len(s.arguments.parameters) == 1
    assert json.loads(s.with_param) == items


def test_task_spec_returns_with_single_values(op):
    t = Task("t", op, [{"a": 1}])
    s = t._build_dag_task()

    assert s.name == "t"
    assert s.template == "t"
    assert len(s.arguments.parameters) == 1
    assert s.arguments.parameters[0].name == "a"
    assert s.arguments.parameters[0].value == "{{item.a}}"


def test_task_template_does_not_contain_gpu_references(op):
    t = Task("t", op, [{"a": 1}], resources=Resources())
    tt = t._build_template()

    assert not hasattr(tt, "tolerations")
    assert not hasattr(tt, "retry_strategy")
    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.inputs, IoArgoprojWorkflowV1alpha1Inputs)
    assert not hasattr(tt, "node_selector")


def test_task_template_contains_expected_field_values_and_types(op, affinity):
    t = Task(
        "t",
        op,
        [{"a": 1}],
        resources=Resources(gpus=1),
        tolerations=[GPUToleration],
        node_selectors={"abc": "123-gpu"},
        retry=Retry(duration=1, max_duration=2),
        daemon=True,
        affinity=affinity,
        memoize=Memoize("a", "b", "1h"),
    )
    tt = t._build_template()

    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.inputs, IoArgoprojWorkflowV1alpha1Inputs)
    assert not hasattr(tt, "node_selectors")
    assert isinstance(tt.tolerations, list)
    assert isinstance(tt.daemon, bool)
    assert all([isinstance(x, _ArgoToleration) for x in tt.tolerations])
    assert tt.name == "t"
    assert (
        tt.script.source == "import os\nimport sys\nsys.path.append(os.getcwd())\n"
        "import json\n"
        "try: a = json.loads('''{{inputs.parameters.a}}''')\n"
        "except: a = '''{{inputs.parameters.a}}'''\n"
        "\n"
        "print(a)\n"
    )
    assert tt.inputs.parameters[0].name == "a"
    assert len(tt.tolerations) == 1
    assert tt.tolerations[0].key == "nvidia.com/gpu"
    assert tt.tolerations[0].effect == "NoSchedule"
    assert tt.tolerations[0].operator == "Equal"
    assert tt.tolerations[0].value == "present"
    assert tt.retry_strategy is not None
    assert tt.retry_strategy.backoff.duration == "1"
    assert tt.retry_strategy.backoff.max_duration == "2"
    assert tt.daemon
    assert hasattr(tt, "node_selector")
    assert not hasattr(tt, "container")
    assert hasattr(tt, "affinity")
    assert tt.affinity is not None
    assert hasattr(tt, "memoize")


def test_task_template_does_not_add_affinity_when_none(no_op):
    t = Task("t", no_op)
    tt = t._build_template()

    assert not hasattr(tt, "affinity")


def test_task_template_contains_expected_retry_strategy(no_op):
    r = Retry(duration=3, max_duration=9)
    t = Task("t", no_op, retry=r)
    assert t.retry.duration == 3
    assert t.retry.max_duration == 9

    tt = t._build_template()
    tr = t._build_retry_strategy()

    template_backoff = tt.retry_strategy.backoff
    retry_backoff = tr.backoff

    assert int(template_backoff.duration) == int(retry_backoff.duration)
    assert int(template_backoff.max_duration) == int(retry_backoff.max_duration)


def test_task_get_retry_returns_expected_none(no_op):
    t = Task("t", no_op)

    tr = t._build_retry_strategy()
    assert tr is None


def test_task_sets_kwarg(kwarg_op, kwarg_multi_op):
    t = Task("t", kwarg_op)
    generated_input = t.inputs[0]
    assert isinstance(generated_input, Parameter)
    assert generated_input.name == "a"
    assert generated_input.default == "42"

    t = Task("t", kwarg_multi_op, [{"a": 50}])
    generated_input_1 = t.inputs[0]
    assert isinstance(generated_input, Parameter)
    assert generated_input_1.name == "a"
    assert generated_input_1.value == "{{item.a}}"

    generated_input_2 = t.inputs[1]
    assert isinstance(generated_input, Parameter)
    assert generated_input_2.name == "b"
    assert generated_input_2.value == "43"


def test_task_fails_artifact_validation(no_op, artifact):
    with pytest.raises(AssertionError) as e:
        Task("t", no_op, inputs=[artifact, artifact])
    assert str(e.value) == "input objects must have unique names"


def test_task_artifact_returns_expected_list(no_op, artifact):
    t = Task("t", no_op, inputs=[artifact])

    artifact = t.inputs[0].as_input()
    assert artifact.name == artifact.name
    assert artifact.path == artifact.path


def test_task_adds_s3_input_artifact():
    t = Task("t", inputs=[S3Artifact("n", "/p", "s3://my-bucket", "key")])

    artifact = t.inputs[0].as_input()
    assert artifact.name == "n"
    assert artifact.s3.bucket == "s3://my-bucket"
    assert artifact.s3.key == "key"


def test_task_adds_gcs_input_artifact():
    t = Task("t", inputs=[GCSArtifact("n", "/p", "gs://my-bucket", "key")])

    artifact = t.inputs[0].as_input()
    assert artifact.name == "n"
    assert artifact.gcs.bucket == "gs://my-bucket"
    assert artifact.gcs.key == "key"


def test_task_adds_git_input_artifact():
    t = Task(
        "t",
        inputs=[GitArtifact("r", "/my-repo", "https://github.com/argoproj/argo-workflows.git", "master")],
    )

    artifact = t.inputs[0].as_input()
    assert artifact
    assert artifact.name == "r"
    assert artifact.path == "/my-repo"
    assert artifact.git.repo == "https://github.com/argoproj/argo-workflows.git"
    assert artifact.git.revision == "master"


@pytest.fixture
def task_security_context_kwargs():
    sc_kwargs = {
        "run_as_user": 1000,
        "run_as_group": 1001,
        "run_as_non_root": False,
        "additional_capabilities": ["SYS_RAWIO"],
    }
    return sc_kwargs


def test_task_contains_specified_security_context(no_op, task_security_context_kwargs):
    tsc = TaskSecurityContext(**task_security_context_kwargs)
    t = Task("t", no_op, security_context=tsc)
    additional_capabilities = task_security_context_kwargs["additional_capabilities"]
    expected_capabilities = Capabilities(add=additional_capabilities)
    task_security_context_kwargs.pop("additional_capabilities")
    expected_security_context = SecurityContext(
        **task_security_context_kwargs,
        capabilities=expected_capabilities,
    )
    script_def = t._build_script()
    assert script_def
    assert script_def.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "run_as_non_root", "additional_capabilities"])
def test_task_specified_partial_security_context(no_op, set_only, task_security_context_kwargs):
    one_param_kwargs = {set_only: task_security_context_kwargs[set_only]}
    tsc = TaskSecurityContext(**one_param_kwargs)
    t = Task("t", no_op, security_context=tsc)
    if set_only == "additional_capabilities":
        expected_security_context = SecurityContext()
        additional_capabilities = task_security_context_kwargs["additional_capabilities"]
        expected_capabilities = Capabilities(add=additional_capabilities)
        setattr(expected_security_context, "capabilities", expected_capabilities)
    else:
        expected_security_context = SecurityContext(**one_param_kwargs)
    script_def = t._build_script()
    assert script_def
    assert script_def.security_context == expected_security_context


def test_task_does_not_contain_specified_security_context(no_op):
    t = Task("t", no_op)

    script_def = t._build_script()
    assert script_def
    assert "security_context" not in script_def


def test_task_template_has_correct_labels(op):
    t = Task("t", op, [{"a": 1}], resources=Resources(), labels={"foo": "bar"})
    tt = t._build_template()
    expected_labels = {"foo": "bar"}
    assert tt.metadata.labels == expected_labels


def test_task_template_has_correct_annotations(op):
    t = Task("t", op, [{"a": 1}], resources=Resources(), annotations={"foo": "bar"})
    tt = t._build_template()
    expected_annotations = {"foo": "bar"}
    assert tt.metadata.annotations == expected_annotations


def test_task_with_config_map_env_variable(no_op):
    t = Task("t", no_op, env=[ConfigMapEnvSpec(name="n", config_map_name="cn", config_map_key="k")])
    tt = t._build_template()
    assert tt.script.env[0].value_from.config_map_key_ref.name == "cn"
    assert tt.script.env[0].value_from.config_map_key_ref.key == "k"


def test_task_with_config_map_env_from(no_op):
    t = Task("t", no_op, env=[ConfigMapEnvFromSpec(prefix="p", config_map_name="cn")])
    tt = t._build_template()
    assert tt.script.env_from[0].prefix == "p"
    assert tt.script.env_from[0].config_map_ref.name == "cn"


def test_task_should_create_task_with_container_template():
    t = Task("t", command=["cowsay"], resources=Resources(memory_request="4Gi"))
    tt = t._build_template()

    assert tt.container.image == "python:3.7"
    assert tt.container.command[0] == "cowsay"
    assert tt.container.resources["request"]["memory"] == "4Gi"


def test_task_allow_subclassing_when_assigned_next(no_op):
    class SubclassTask(Task):
        pass

    t = SubclassTask("t", no_op)
    t2 = Task("t2", no_op)
    t.next(t2)
    assert t2.depends == "t"


def test_supply_args():
    t = Task("t", args=["arg"])
    tt = t._build_template()
    assert tt.container.args == ["arg"]
    assert "command" not in tt.container


def test_task_script_def_volume_template(no_op):
    t = Task("t", no_op, volumes=[Volume(size="1Gi", mount_path="/tmp")])

    template = t._build_script()
    assert template
    assert len(template.volume_mounts) == 1
    assert template.volume_mounts[0].mount_path == "/tmp"


def test_task_adds_custom_resources(no_op):
    t = Task(
        "t",
        no_op,
        resources=Resources(
            custom_resources={
                "custom-1": "1",
                "custom-2": "42Gi",
            }
        ),
    )
    r = t.resources.build()
    assert r
    assert r["custom-1"] == "1"
    assert r["custom-2"] == "42Gi"


def test_task_adds_variable_as_env_var():
    t = Task("t")
    t1 = Task("t1", "print(42)", env=[EnvSpec(name="IP", value_from_input=t.ip)])
    t1s = t1._build_script()

    assert t1s.env[0].name == "IP"
    assert t1s.env[0].value == "{{inputs.parameters.IP}}"

    t1g = t1.build_arguments()
    assert t1g
    assert t1g.parameters[0].name == "IP"
    assert t1g.parameters[0].value == "{{tasks.t.ip}}"


def test_task_adds_other_task_on_success():
    t = Task("t")
    o = Task("o")

    t.on_success(o)
    assert o.depends == f"t.{TaskResult.Succeeded}"


def test_task_adds_other_task_on_failure():
    t = Task("t")
    o = Task("o")

    t.on_failure(o)
    assert o.depends == f"t.{TaskResult.Failed}"


def test_task_adds_other_task_on_error():
    t = Task("t")
    o = Task("o")

    t.on_error(o)
    assert o.depends == f"t.{TaskResult.Errored}"


def test_task_has_expected_retry_limit():
    t = Task("t", retry=Retry(limit=5))
    tt = t._build_template()
    assert tt.retry_strategy.limit == "5"


def test_task_has_expected_retry_policy():
    t = Task("t", retry=Retry(retry_policy=RetryPolicy.Always))
    tt = t._build_template()
    assert tt.retry_strategy.retry_policy == "Always"


def test_task_uses_expected_template_ref():
    t = Task("t", template_ref=TemplateRef(name="workflow-template", template="template"))._build_dag_task()
    assert hasattr(t, "template_ref")
    assert t.template_ref.name == "workflow-template"
    assert t.template_ref.template == "template"


def test_task_does_not_include_imports_when_no_params_are_specified(no_op):
    t = Task("t", no_op)
    t_script = t._get_script()
    assert "import json" not in t_script
    assert "pass\n" in t_script


def test_task_adds_exit_condition(no_op):
    t = Task("t", no_op)
    t.on_workflow_status(Operator.Equals, WorkflowStatus.Succeeded)
    assert t.when == "{{workflow.status}} == Succeeded"


def test_all_failed_adds_dependency(no_op, multi_op):
    t1 = Task(
        "t1",
        multi_op,
        with_param=[
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    t2 = Task("t2", no_op)
    t1.when_all_failed(t2)
    assert t2.depends == "t1.AllFailed"

    t1 = Task(
        "t1",
        multi_op,
        with_param=[
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    t2 = Task("t2", no_op)
    t3 = Task("t3", no_op)
    t2 >> t3
    t1.when_all_failed(t3)
    assert t3.depends == "t2 && t1.AllFailed"
    # calling again hits the block that checks it's already added
    with pytest.raises(ValueError) as e:
        t2 >> t3
    assert str(e.value) == "t2 already in t3's depends: t2 && t1.AllFailed"
    with pytest.raises(ValueError) as e:
        t1.when_all_failed(t3)
    assert str(e.value) == "t1 already in t3's depends: t2 && t1.AllFailed"
    assert t3.depends == "t2 && t1.AllFailed"

    # now set a new dependency to ensure that the `depends` field is used
    t4 = Task("t4", no_op)
    t4 >> t3
    assert t3.depends == "t2 && t1.AllFailed && t4"


def test_any_succeeded_adds_dependency(no_op, multi_op):
    t1 = Task(
        "t1",
        multi_op,
        with_param=[
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    t2 = Task("t2", no_op)
    t1.when_any_succeeded(t2)
    assert t2.depends == "t1.AnySucceeded"

    t1 = Task(
        "t1",
        multi_op,
        with_param=[
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 3},
        ],
    )
    t2 = Task("t2", no_op)
    t3 = Task("t3", no_op)
    t2 >> t3
    t1.when_any_succeeded(t3)
    assert t3.depends == "t2 && t1.AnySucceeded"
    # calling again hits the block that checks it's already added
    with pytest.raises(ValueError) as e:
        t2 >> t3
    assert str(e.value) == "t2 already in t3's depends: t2 && t1.AnySucceeded"
    with pytest.raises(ValueError) as e:
        t1.when_any_succeeded(t3)
    assert str(e.value) == "t1 already in t3's depends: t2 && t1.AnySucceeded"
    assert t3.depends == "t2 && t1.AnySucceeded"

    # now set a new dependency to ensure that the `depends` field is used
    t4 = Task("t4", no_op)
    t4 >> t3
    assert t3.depends == "t2 && t1.AnySucceeded && t4"


def test_task_fails_to_validate_with_incorrect_memoize(op):
    with pytest.raises(AssertionError) as e:
        Task("t", op, with_param=[{"a": 42}], memoize=Memoize("b", "a", "a-key"))
    assert str(e.value) == "memoize key must be a parameter of the function"


def test_task_template_contains_resource_template():
    resource_template = ResourceTemplate(action="create")
    t = Task(name="t", resource_template=resource_template)
    tt = t._build_template()
    resource = resource_template.build()
    assert tt.resource == resource
