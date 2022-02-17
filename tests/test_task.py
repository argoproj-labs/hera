import pytest
from argo_workflows.model.capabilities import Capabilities
from argo_workflows.model.security_context import SecurityContext
from argo_workflows.models import IoArgoprojWorkflowV1alpha1Inputs
from argo_workflows.models import Toleration as _ArgoToleration
from pydantic import ValidationError

from hera.artifact import GCSArtifact, S3Artifact
from hera.env import ConfigMapEnvSpec
from hera.input import InputFrom
from hera.operator import Operator
from hera.resources import Resources
from hera.retry import Retry
from hera.security_context import TaskSecurityContext
from hera.task import Task
from hera.toleration import GPUToleration, Toleration
from hera.variable import VariableAsEnv
from hera.volumes import ConfigMapVolume, EmptyDirVolume, ExistingVolume, Volume


def test_next_and_shifting_set_correct_dependencies(no_op):
    t1, t2, t3 = Task('t1', no_op), Task('t2', no_op), Task('t3', no_op)
    t1.next(t2).next(t3)
    assert t2.argo_task.dependencies == ['t1']
    assert t3.argo_task.dependencies == ['t2']

    t4, t5, t6 = Task('t4', no_op), Task('t5', no_op), Task('t6', no_op)
    t4 >> t5 >> t6
    assert t5.argo_task.dependencies == ['t4']
    assert t6.argo_task.dependencies == ['t5']


def test_when_correct_expression_and_dependencies(no_op):
    t1, t2, t3 = Task('t1', no_op), Task('t2', no_op), Task('t3', no_op)
    t2.when(t1, Operator.equals, "t2")
    t3.when(t1, Operator.equals, "t3")

    assert t2.argo_task.dependencies == ['t1']
    assert t3.argo_task.dependencies == ['t1']

    assert t2.argo_task.when == "{{tasks.t1.outputs.result}} == t2"
    assert t3.argo_task.when == "{{tasks.t1.outputs.result}} == t3"


def test_retry_limits_fail_validation():
    with pytest.raises(ValidationError):
        Retry(duration=5, max_duration=4)


def test_func_and_func_param_validation_raises_on_args_not_passed(op):
    with pytest.raises(AssertionError) as e:
        Task('t', op, [])
    assert str(e.value) == 'no parameters passed for function'


def test_func_and_func_param_validation_raises_on_difference(op):
    with pytest.raises(AssertionError) as e:
        Task('t', op, [{'a': 1}, {'b': 1}])
    assert str(e.value) == 'mismatched function arguments and passed parameters'


def test_param_getter_returns_empty(no_op):
    t = Task('t', no_op)
    assert not t.get_parameters()


def test_param_getter_parses_on_multi_params(op):
    t = Task('t', op, [{'a': 1}, {'a': 2}, {'a': 3}])
    params = t.get_parameters()
    for p in params:
        assert p.name == 'a'
        assert p.value == '{{item.a}}'


def test_param_getter_parses_single_param_val_on_json_payload(op):
    t = Task('t', op, [{'a': 1}])
    param = t.get_parameters()[0]
    assert param.name == 'a'
    assert param.value == '1'  # from json.dumps


def test_param_getter_parses_single_param_val_on_base_model_payload(mock_model, op):
    t = Task('t', op, [{'a': mock_model()}])
    param = t.get_parameters()[0]
    assert param.name == 'a'
    assert param.value == '{"field1": 1, "field2": 2}'


def test_param_script_portion_adds_formatted_json_calls(op):
    t = Task('t', op, [{'a': 1}])
    script = t.get_param_script_portion()
    assert script == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n'


def test_script_getter_returns_expected_string(op, typed_op):
    t = Task('t', op, [{'a': 1}])
    script = t.get_script()
    assert script == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n\nprint(a)\n'

    t = Task('t', typed_op, [{'a': 1}])
    script = t.get_script()
    assert script == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n\nprint(a)\nreturn [{\'a\': (a, a)}]\n'


def test_script_getter_parses_multi_line_function(long_op):
    t = Task(
        't',
        long_op,
        [
            {
                'very_long_parameter_name': 1,
                'very_very_long_parameter_name': 2,
                'very_very_very_long_parameter_name': 3,
                'very_very_very_very_long_parameter_name': 4,
                'very_very_very_very_very_long_parameter_name': 5,
            }
        ],
    )

    expected_script = """import json
very_long_parameter_name = json.loads('{{inputs.parameters.very_long_parameter_name}}')
very_very_long_parameter_name = json.loads('{{inputs.parameters.very_very_long_parameter_name}}')
very_very_very_long_parameter_name = json.loads('{{inputs.parameters.very_very_very_long_parameter_name}}')
very_very_very_very_long_parameter_name = json.loads('{{inputs.parameters.very_very_very_very_long_parameter_name}}')
very_very_very_very_very_long_parameter_name = json.loads('{{inputs.parameters.very_very_very_very_very_long_parameter_name}}')

print(42)
"""
    script = t.get_script()
    assert script == expected_script


def test_resources_returned_with_appropriate_limits(op):
    r = Resources()
    t = Task('t', op, [{'a': 1}], resources=r)
    resources = t.get_resources()

    assert resources.limits['cpu'] == '1'
    assert resources.limits['memory'] == '4Gi'


def test_resources_returned_with_gpus(op):
    r = Resources(gpus=2)
    t = Task('t', op, [{'a': 1}], resources=r)
    resources = t.get_resources()

    assert resources.requests['nvidia.com/gpu'] == '2'
    assert resources.limits['nvidia.com/gpu'] == '2'


def test_parallel_items_assemble_base_models(multi_op, mock_model):
    t = Task(
        't',
        multi_op,
        [
            {'a': 1, 'b': {'d': 2, 'e': 3}, 'c': mock_model()},
            {'a': 1, 'b': {'d': 2, 'e': 3}, 'c': mock_model()},
            {'a': 1, 'b': {'d': 2, 'e': 3}, 'c': mock_model()},
        ],
    )
    items = t.get_parallel_items()
    for item in items:
        assert item.value['a'] == '1'
        assert item.value['b'] == '{"d": 2, "e": 3}'
        assert item.value['c'] == '{"field1": 1, "field2": 2}'


def test_volume_mounts_returns_expected_volumes(no_op):
    r = Resources(
        volumes=[
            Volume(name='v1', size='1Gi', mount_path='/v1'),
            ExistingVolume(name='v2', mount_path='/v2'),
            EmptyDirVolume(name='v3'),
            ConfigMapVolume(config_map_name="cfm", mount_path="/v3"),
        ],
    )
    t = Task('t', no_op, resources=r)
    vs = t.get_volume_mounts()
    assert vs[0].name == 'v1'
    assert vs[0].mount_path == '/v1'
    assert vs[1].name == 'v2'
    assert vs[1].mount_path == '/v2'
    assert vs[2].name == 'v3'
    assert vs[2].mount_path == '/dev/shm'
    assert vs[3].name
    assert vs[3].mount_path == "/v3"


def test_gpu_toleration_returns_expected_toleration():
    tn = GPUToleration
    assert tn.key == 'nvidia.com/gpu'
    assert tn.effect == 'NoSchedule'
    assert tn.operator == 'Equal'
    assert tn.value == 'present'


def test_task_with_default_value_in_toleration(no_op):
    toleration = Toleration(key="nvidia.com/gpu", effect="NoSchedule", operator="Equal")
    t = Task('t', no_op, tolerations=[toleration])

    assert t.tolerations[0].value == ""
    assert t.tolerations[0].key == 'nvidia.com/gpu'
    assert t.tolerations[0].effect == 'NoSchedule'
    assert t.tolerations[0].operator == 'Equal'


def test_task_command_parses(mock_model, op):
    t = Task('t', op, func_params=[{'a': mock_model()}])
    assert t.get_command() == ['python']


def test_task_spec_returns_with_parallel_items(op):
    t = Task('t', op, [{'a': 1}, {'a': 1}, {'a': 1}])
    s = t.get_task_spec()
    items = [{'a': '1'}, {'a': '1'}, {'a': '1'}]

    assert s.name == 't'
    assert s.template == 't'
    assert len(s.arguments.parameters) == 1
    assert len(s.with_items) == 3
    assert [i.value for i in s.with_items] == items


def test_task_spec_returns_with_single_values(op):
    t = Task('t', op, [{'a': 1}])
    s = t.get_task_spec()

    assert s.name == 't'
    assert s.template == 't'
    assert len(s.arguments.parameters) == 1
    assert s.arguments.parameters[0].name == 'a'
    assert s.arguments.parameters[0].value == '1'


def test_task_template_does_not_contain_gpu_references(op):
    t = Task('t', op, [{'a': 1}], resources=Resources())
    tt = t.get_task_template()

    assert tt.tolerations == []
    assert not hasattr(tt, 'retry_strategy')
    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.inputs, IoArgoprojWorkflowV1alpha1Inputs)
    assert not hasattr(tt, 'node_selector')


def test_task_template_contains_expected_field_values_and_types(op):
    t = Task(
        't',
        op,
        [{'a': 1}],
        resources=Resources(gpus=1),
        tolerations=[GPUToleration],
        node_selectors={'abc': '123-gpu'},
        retry=Retry(duration=1, max_duration=2),
        daemon=True,
    )
    tt = t.get_task_template()

    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.inputs, IoArgoprojWorkflowV1alpha1Inputs)
    assert not hasattr(tt, 'node_selectors')
    assert isinstance(tt.tolerations, list)
    assert isinstance(tt.daemon, bool)
    assert all([isinstance(x, _ArgoToleration) for x in tt.tolerations])
    assert tt.name == 't'
    assert tt.script.source == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n\nprint(a)\n'
    assert tt.inputs.parameters[0].name == 'a'
    assert len(tt.tolerations) == 1
    assert tt.tolerations[0].key == 'nvidia.com/gpu'
    assert tt.tolerations[0].effect == 'NoSchedule'
    assert tt.tolerations[0].operator == 'Equal'
    assert tt.tolerations[0].value == 'present'
    assert tt.retry_strategy is not None
    assert tt.retry_strategy.backoff.duration == '1'
    assert tt.retry_strategy.backoff.max_duration == '2'
    assert tt.daemon
    assert hasattr(tt, 'node_selector')
    assert not hasattr(tt, 'container')


def test_task_template_contains_expected_retry_strategy(no_op):
    r = Retry(duration=3, max_duration=9)
    t = Task('t', no_op, retry=r)
    assert t.retry.duration == 3
    assert t.retry.max_duration == 9

    tt = t.get_task_template()
    tr = t.get_retry_strategy()

    template_backoff = tt.retry_strategy.backoff
    retry_backoff = tr.backoff

    assert int(template_backoff.duration) == int(retry_backoff.duration)
    assert int(template_backoff.max_duration) == int(retry_backoff.max_duration)


def test_task_get_retry_returns_expected_none(no_op):
    t = Task('t', no_op)

    tr = t.get_retry_strategy()
    assert tr is None


def test_task_sets_user_kwarg_override(kwarg_op):
    t = Task('t', kwarg_op, [{'a': 43}])
    assert t.parameters[0].name == 'a'
    assert t.parameters[0].value == '43'


def test_task_sets_kwarg(kwarg_op, kwarg_multi_op):
    t = Task('t', kwarg_op)
    assert t.parameters[0].name == 'a'
    assert t.parameters[0].value == '42'

    t = Task('t', kwarg_multi_op, [{'a': 50}])
    assert t.parameters[0].name == 'a'
    assert t.parameters[0].value == '50'
    assert t.parameters[1].name == 'b'
    assert t.parameters[1].value == '43'


def test_task_fails_artifact_validation(no_op, in_artifact):
    with pytest.raises(AssertionError) as e:
        Task('t', no_op, input_artifacts=[in_artifact, in_artifact])
    assert str(e.value) == 'input artifact names must be unique'


def test_task_validation_fails_on_input_from_plus_input_artifact(op, in_artifact):
    with pytest.raises(AssertionError) as e:
        Task('t', op, input_from=InputFrom(name='test', parameters=['a']), input_artifacts=[in_artifact])
    assert str(e.value) == 'cannot supply both InputFrom and Artifacts'


def test_task_input_artifact_returns_expected_list(no_op, in_artifact):
    t = Task('t', no_op, input_artifacts=[in_artifact])

    artifact = t.inputs.artifacts[0]
    assert artifact.name == in_artifact.name
    assert artifact.path == in_artifact.path


def test_task_adds_s3_input_artifact():
    t = Task('t', input_artifacts=[S3Artifact(name="n", path="/p", key="key")])

    artifact = t.inputs.artifacts[0]
    assert artifact.name == "n"
    assert artifact.s3.key == "key"


def test_task_adds_gcs_input_artifact():
    t = Task('t', input_artifacts=[GCSArtifact(name="n", path="/p", key="key")])

    artifact = t.inputs.artifacts[0]
    assert artifact.name == "n"
    assert artifact.gcs.key == "key"


def test_task_output_artifact_returns_expected_list(no_op, out_artifact):
    t = Task('t', no_op, output_artifacts=[out_artifact])

    artifact = t.outputs.artifacts[0]
    assert artifact.name == out_artifact.name
    assert artifact.path == out_artifact.path


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
    t = Task('t', no_op, security_context=tsc)
    additional_capabilities = task_security_context_kwargs["additional_capabilities"]
    expected_capabilities = Capabilities(add=additional_capabilities)
    task_security_context_kwargs.pop("additional_capabilities")
    expected_security_context = SecurityContext(
        **task_security_context_kwargs,
        capabilities=expected_capabilities,
    )
    assert t.argo_template.script.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "run_as_non_root", "additional_capabilities"])
def test_task_specified_partial_security_context(no_op, set_only, task_security_context_kwargs):
    one_param_kwargs = {set_only: task_security_context_kwargs[set_only]}
    tsc = TaskSecurityContext(**one_param_kwargs)
    t = Task('t', no_op, security_context=tsc)
    if set_only == "additional_capabilities":
        expected_security_context = SecurityContext()
        additional_capabilities = task_security_context_kwargs["additional_capabilities"]
        expected_capabilities = Capabilities(add=additional_capabilities)
        setattr(expected_security_context, "capabilities", expected_capabilities)
    else:
        expected_security_context = SecurityContext(**one_param_kwargs)
    assert t.argo_template.script.security_context == expected_security_context


def test_task_does_not_contain_specified_security_context(no_op):
    t = Task('t', no_op)

    assert "security_context" not in t.argo_template.script


def test_task_template_has_correct_labels(op):
    t = Task('t', op, [{'a': 1}], resources=Resources(), labels={'foo': 'bar'})
    tt = t.get_task_template()
    expected_labels = {'foo': 'bar'}
    assert tt.metadata.labels == expected_labels


def test_task_with_config_map_env_variable(no_op):
    t = Task('t', no_op, env_specs=[ConfigMapEnvSpec(name="n", config_map_name="cn", config_map_key="k")])
    tt = t.get_task_template()
    assert tt.script.env[0].value_from.config_map_key_ref.name == "cn"
    assert tt.script.env[0].value_from.config_map_key_ref.key == "k"


def test_task_should_create_task_with_container_template():
    t = Task('t', command=["cowsay"])
    tt = t.get_task_template()

    assert tt.container.image == "python:3.7"
    assert tt.container.command[0] == "cowsay"
    assert tt.container.resources.requests["memory"] == '4Gi'


def test_task_allow_subclassing_when_assigned_next(no_op):
    class SubclassTask(Task):
        pass

    t = SubclassTask('t', no_op)
    t2 = Task('t2', no_op)
    t.next(t2)
    assert t2.argo_task.dependencies[0] == 't'


def test_supply_args():
    t = Task('t', args=["arg"])
    assert t.argo_template.container.args == ["arg"]
    assert 'command' not in t.argo_template.container


def test_task_script_def_volume_template(no_op):
    t = Task('t', no_op, resources=Resources(volumes=[Volume(size="1Gi", mount_path="/tmp")]))

    template = t.get_script_def()
    assert len(template.volume_mounts) == 1
    assert template.volume_mounts[0].mount_path == "/tmp"


def test_task_adds_custom_resources(no_op):
    t = Task(
        't',
        no_op,
        resources=Resources(
            min_custom_resources={
                'custom-1': '1',
                'custom-2': '42Gi',
            }
        ),
    )
    r = t.get_resources()

    assert r.requests['cpu'] == '1'
    assert r.requests['memory'] == '4Gi'
    assert r.requests['custom-1'] == '1'
    assert r.requests['custom-2'] == '42Gi'

    assert r.limits['cpu'] == '1'
    assert r.limits['memory'] == '4Gi'
    assert r.limits['custom-1'] == '1'
    assert r.limits['custom-2'] == '42Gi'


def test_task_adds_variable_as_env_var():
    t = Task('t')
    t1 = Task('t1', variables=[VariableAsEnv(name="IP", value=t.ip)])

    assert t1.env[0].name == "IP"
    assert t1.env[0].value == "{{inputs.parameters.IP}}"

    assert t1.arguments.parameters[0].name == "IP"
    assert t1.arguments.parameters[0].value == "\"{{tasks.t.ip}}\""
