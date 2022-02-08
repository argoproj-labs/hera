import pytest
from argo.workflows.client import V1alpha1Arguments, V1alpha1Inputs, V1Toleration
from pydantic import ValidationError

from hera.input import InputFrom
from hera.operator import Operator
from hera.resources import Resources
from hera.retry import Retry
from hera.task import Task
from hera.toleration import GPUToleration, Toleration
from hera.volumes import EmptyDirVolume, ExistingVolume, Volume


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

    assert t2.argo_task._when == "{{tasks.t1.outputs.result}} == t2"
    assert t3.argo_task._when == "{{tasks.t1.outputs.result}} == t3"


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
        assert item['a'] == '1'
        assert item['b'] == '{"d": 2, "e": 3}'
        assert item['c'] == '{"field1": 1, "field2": 2}'


def test_volume_mounts_returns_expected_volumes(no_op):
    r = Resources(
        volume=Volume(name='v1', size='1Gi', mount_path='/v1'),
        existing_volume=ExistingVolume(name='v2', mount_path='/v2'),
        empty_dir_volume=EmptyDirVolume(name='v3'),
    )
    t = Task('t', no_op, resources=r)
    vs = t.get_volume_mounts()
    assert vs[0].name == 'v1'
    assert vs[0].mount_path == '/v1'
    assert vs[1].name == 'v2'
    assert vs[1].mount_path == '/v2'
    assert vs[2].name == 'v3'
    assert vs[2].mount_path == '/dev/shm'


def test_gpu_toleration_returns_expected_toleration():
    tn = GPUToleration
    assert tn.key == 'nvidia.com/gpu'
    assert tn.effect == 'NoSchedule'
    assert tn.operator == 'Equal'
    assert tn.value == 'present'


def test_task_with_default_value_in_toleration(no_op):
    toleration = Toleration(key="nvidia.com/gpu", effect="NoSchedule", operator="Equal")
    t = Task('t', no_op, tolerations=[toleration])

    assert t.tolerations[0].value == None


def test_task_command_parses(mock_model, op):
    t = Task('t', op, [{'a': mock_model()}])
    assert t.get_command() == ['python']


def test_task_spec_returns_with_parallel_items(op):
    t = Task('t', op, [{'a': 1}, {'a': 1}, {'a': 1}])
    s = t.get_task_spec()
    items = [{'a': '1'}, {'a': '1'}, {'a': '1'}]

    assert s.name == 't'
    assert s.template == 't'
    assert len(s.arguments.parameters) == 1
    assert len(s.with_items) == 3
    assert s.with_items == items


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

    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.arguments, V1alpha1Arguments)
    assert isinstance(tt.inputs, V1alpha1Inputs)
    assert tt.node_selector is None
    assert tt.tolerations is None
    assert tt.retry_strategy is None


def test_task_template_contains_expected_field_values_and_types(op):
    t = Task(
        't',
        op,
        [{'a': 1}],
        resources=Resources(gpus=1),
        tolerations=[GPUToleration],
        node_selectors={'abc': '123-gpu'},
        retry=Retry(duration=1, max_duration=2),
    )
    tt = t.get_task_template()

    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.arguments, V1alpha1Arguments)
    assert isinstance(tt.inputs, V1alpha1Inputs)
    assert isinstance(tt.node_selector, dict)
    assert isinstance(tt.tolerations, list)
    assert all([isinstance(x, V1Toleration) for x in tt.tolerations])
    assert tt.name == 't'
    assert tt.script.source == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n\nprint(a)\n'
    assert tt.arguments.parameters[0].name == 'a'
    assert tt.inputs.parameters[0].name == 'a'
    assert len(tt.tolerations) == 1
    assert tt.tolerations[0].key == 'nvidia.com/gpu'
    assert tt.tolerations[0].effect == 'NoSchedule'
    assert tt.tolerations[0].operator == 'Equal'
    assert tt.tolerations[0].value == 'present'
    assert tt.retry_strategy is not None
    assert tt.retry_strategy.backoff.duration == '1'
    assert tt.retry_strategy.backoff.max_duration == '2'


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


def test_task_input_artifact_returns_expected_list(no_op, out_artifact, in_artifact):
    t = Task('t', no_op, input_artifacts=[in_artifact])

    artifact = t.inputs.artifacts[0]
    assert artifact._from is None
    assert artifact.name == in_artifact.name
    assert artifact.path == in_artifact.path


def test_task_output_artifact_returns_expected_list(no_op, out_artifact):
    t = Task('t', no_op, output_artifacts=[out_artifact])

    artifact = t.outputs.artifacts[0]
    assert artifact.name == out_artifact.name
    assert artifact.path == out_artifact.path


def test_task_security_context():
    assert False