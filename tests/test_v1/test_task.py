from typing import Dict, List, Tuple

import pytest
from argo.workflows.client import V1alpha1Arguments, V1alpha1Inputs, V1Toleration
from pydantic import BaseModel, ValidationError

from hera.v1.empty_dir_volume import EmptyDirVolume
from hera.v1.existing_volume import ExistingVolume
from hera.v1.resources import Resources
from hera.v1.retry import Retry
from hera.v1.task import Task
from hera.v1.toleration import GPUToleration
from hera.v1.volume import Volume
from hera.v1.operator import Operator


class MockModel(BaseModel):
    field1: int = 1
    field2: int = 2


def noop():
    pass


def op(a):
    print(a)


def kwarg_op(a: int = 42):
    print(a)


def kwarg_multi_op(a: int = 42, b: int = 43):
    print(a, b)


def multiop(a, b, c):
    print(a, b, c)


def typedop(a) -> List[Dict[str, Tuple[int, int]]]:
    print(a)
    return [{'a': (a, a)}]


def longop(
    very_long_parameter_name,
    very_very_long_parameter_name,
    very_very_very_long_parameter_name,
    very_very_very_very_long_parameter_name,
    very_very_very_very_very_long_parameter_name,
):
    print(42)


def test_next_and_shifting_set_correct_dependencies():
    t1, t2, t3 = Task('t1', noop), Task('t2', noop), Task('t3', noop)
    t1.next(t2).next(t3)
    assert t2.argo_task.dependencies == ['t1']
    assert t3.argo_task.dependencies == ['t2']

    t4, t5, t6 = Task('t4', noop), Task('t5', noop), Task('t6', noop)
    t4 >> t5 >> t6
    assert t5.argo_task.dependencies == ['t4']
    assert t6.argo_task.dependencies == ['t5']


def test_when_correct_expression_and_dependencies():
    t1, t2, t3 = Task('t1', noop), Task('t2', noop), Task('t3', noop)
    t2.when(t1, Operator.equals, "t2")
    t3.when(t1, Operator.equals, "t3")

    assert t2.argo_task.dependencies == ['t1']
    assert t3.argo_task.dependencies == ['t1']

    assert t2.argo_task._when == "{{tasks.t1.outputs.result}} == t2"
    assert t3.argo_task._when == "{{tasks.t1.outputs.result}} == t3"


def test_retry_limits_fail_validation():
    with pytest.raises(ValidationError):
        Retry(duration=5, max_duration=4)


def test_func_and_func_param_validation_raises_on_args_not_passed():
    with pytest.raises(AssertionError) as e:
        Task('t', op, [])
    assert str(e.value) == 'no parameters passed for function'


def test_func_and_func_param_validation_raises_on_difference():
    with pytest.raises(AssertionError) as e:
        Task('t', op, [{'a': 1}, {'b': 1}])
    assert str(e.value) == 'mismatched function arguments and passed parameters'


def test_param_getter_returns_empty():
    t = Task('t', noop)
    assert not t.get_parameters()


def test_param_getter_parses_on_multi_params():
    t = Task('t', op, [{'a': 1}, {'a': 2}, {'a': 3}])
    params = t.get_parameters()
    for p in params:
        assert p.name == 'a'
        assert p.value == '{{item.a}}'


def test_param_getter_parses_single_param_val_on_json_payload():
    t = Task('t', op, [{'a': 1}])
    param = t.get_parameters()[0]
    assert param.name == 'a'
    assert param.value == '1'  # from json.dumps


def test_param_getter_parses_single_param_val_on_base_model_payload():
    t = Task('t', op, [{'a': MockModel()}])
    param = t.get_parameters()[0]
    assert param.name == 'a'
    assert param.value == '{"field1": 1, "field2": 2}'


def test_param_script_portion_adds_formatted_json_calls():
    t = Task('t', op, [{'a': 1}])
    script = t.get_param_script_portion()
    assert script == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n'


def test_script_getter_returns_expected_string():
    t = Task('t', op, [{'a': 1}])
    script = t.get_script()
    assert script == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n\nprint(a)\n'

    t = Task('t', typedop, [{'a': 1}])
    script = t.get_script()
    assert script == 'import json\na = json.loads(\'{{inputs.parameters.a}}\')\n\nprint(a)\nreturn [{\'a\': (a, a)}]\n'


def test_script_getter_parses_multi_line_function():
    t = Task(
        't',
        longop,
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


def test_resources_returned_with_appropriate_limits():
    r = Resources()
    t = Task('t', op, [{'a': 1}], resources=r)
    resources = t.get_resources()

    assert resources.limits['cpu'] == '1'
    assert resources.limits['memory'] == '4Gi'


def test_resources_returned_with_gpus():
    r = Resources(gpus=2)
    t = Task('t', op, [{'a': 1}], resources=r)
    resources = t.get_resources()

    assert resources.requests['nvidia.com/gpu'] == '2'
    assert resources.limits['nvidia.com/gpu'] == '2'


def test_parallel_items_assemble_base_models():
    t = Task(
        't',
        multiop,
        [
            {'a': 1, 'b': {'d': 2, 'e': 3}, 'c': MockModel()},
            {'a': 1, 'b': {'d': 2, 'e': 3}, 'c': MockModel()},
            {'a': 1, 'b': {'d': 2, 'e': 3}, 'c': MockModel()},
        ],
    )
    items = t.get_parallel_items()
    for item in items:
        assert item['a'] == '1'
        assert item['b'] == '{"d": 2, "e": 3}'
        assert item['c'] == '{"field1": 1, "field2": 2}'


def test_volume_mounts_returns_expected_volumes():
    r = Resources(
        volume=Volume(name='v1', size='1Gi', mount_path='/v1'),
        existing_volume=ExistingVolume(name='v2', mount_path='/v2'),
        empty_dir_volume=EmptyDirVolume(name='v3'),
    )
    t = Task('t', noop, resources=r)
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


def test_task_command_parses():
    t = Task('t', op, [{'a': MockModel()}])
    assert t.get_command() == ['python']


def test_task_spec_returns_with_parallel_items():
    t = Task('t', op, [{'a': 1}, {'a': 1}, {'a': 1}])
    s = t.get_task_spec()
    items = [{'a': '1'}, {'a': '1'}, {'a': '1'}]

    assert s.name == 't'
    assert s.template == 't'
    assert len(s.arguments.parameters) == 1
    assert len(s.with_items) == 3
    assert s.with_items == items


def test_task_spec_returns_with_single_values():
    t = Task('t', op, [{'a': 1}])
    s = t.get_task_spec()

    assert s.name == 't'
    assert s.template == 't'
    assert len(s.arguments.parameters) == 1
    assert s.arguments.parameters[0].name == 'a'
    assert s.arguments.parameters[0].value == '1'


def test_task_template_does_not_contain_gpu_references():
    t = Task('t', op, [{'a': 1}], resources=Resources())
    tt = t.get_task_template()

    assert isinstance(tt.name, str)
    assert isinstance(tt.script.source, str)
    assert isinstance(tt.arguments, V1alpha1Arguments)
    assert isinstance(tt.inputs, V1alpha1Inputs)
    assert tt.node_selector is None
    assert tt.tolerations is None
    assert tt.retry_strategy is None


def test_task_template_contains_expected_field_values_and_types():
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


def test_task_template_contains_expected_retry_strategy():
    r = Retry(duration=3, max_duration=9)
    t = Task('t', noop, retry=r)
    assert t.retry.duration == 3
    assert t.retry.max_duration == 9

    tt = t.get_task_template()
    tr = t.get_retry_strategy()

    template_backoff = tt.retry_strategy.backoff
    retry_backoff = tr.backoff

    assert int(template_backoff.duration) == int(retry_backoff.duration)
    assert int(template_backoff.max_duration) == int(retry_backoff.max_duration)


def test_task_get_retry_returns_expected_none():
    t = Task('t', noop)

    tr = t.get_retry_strategy()
    assert tr is None


def test_task_sets_user_kwarg_override():
    t = Task('t', kwarg_op, [{'a': 43}])
    assert t.parameters[0].name == 'a'
    assert t.parameters[0].value == '43'


def test_task_sets_kwarg():
    t = Task('t', kwarg_op)
    assert t.parameters[0].name == 'a'
    assert t.parameters[0].value == '42'

    t = Task('t', kwarg_multi_op, [{'a': 50}])
    assert t.parameters[0].name == 'a'
    assert t.parameters[0].value == '50'
    assert t.parameters[1].name == 'b'
    assert t.parameters[1].value == '43'
