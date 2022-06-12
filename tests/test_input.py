from hera import Input, InputFrom, InputParameter, GlobalInputParameter


def test_input_returns_default_expected_spec():
    i = Input('i')
    assert i.name == 'i'

    s = i.get_spec()
    assert s.name == 'i'


def test_input_param_returns_expected_spec():
    i = InputParameter('i', 't', 'p')

    assert i.name == 'i'
    assert i.from_task == 't'
    assert i.parameter_name == 'p'

    s = i.get_spec()
    assert s.name == 'i'
    assert s.value == '{{tasks.t.outputs.parameters.p}}'


def test_input_from_returns_expected_spec():
    i = InputFrom('i', parameters=['a', 'b', 'c'])
    assert i.name == 'i'
    assert i.parameters == ['a', 'b', 'c']

    s = i.get_spec()
    assert len(s) == 3
    for i, v in enumerate(['a', 'b', 'c']):
        assert s[i].name == v
        assert s[i].value == f'{{{{item.{v}}}}}'


def test_global_parameter_returns_expected_spec():
    i = GlobalInputParameter('p', 'g')
    assert i.name == 'p'
    assert i.parameter_name == 'g'

    s = i.get_spec()
    assert s.name == 'p'
    assert s.value == '{{workflow.parameters.g}}'
