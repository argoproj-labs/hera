from typing import Any

import pytest

from hera.workflows import Parameter, Step, Steps, Workflow, script


@script()
def print_message(continue_on: str = "name-clash-arg"):
    print(continue_on)


def test_script_arg_building_name_clash():
    # WHEN - we have a name clash with a non-arguments-taking parameter
    with pytest.raises(ValueError) as e:
        with Workflow(generate_name="name-clash-", entrypoint="name-clash-example"):
            with Steps(name="name-clash-example"):
                print_message(name="print-message", continue_on=Parameter(name="dummy-name", value="dummy-value"))

    # THEN - we raise the ValueError containing the message
    assert (
        "'continue_on' clashes with Step/Task kwargs. Rename 'continue_on' or pass your Parameter/Artifact through 'arguments' or 'with_param'"
        in str(e)
    )


def test_script_arg_building_using_with_param():
    # WHEN - we use with_param to pass in a value for the "continue_on" name clashing arg
    with Workflow(generate_name="name-clash-", entrypoint="name-clash-example"):
        with Steps(name="name-clash-example"):
            # Test passes a Parameter to with_param rather than a Dict
            print_message_step: Step = print_message(
                name="print-message", with_param=Parameter(name="dummy-name", value="test-value")
            )

            # THEN - with_param is populated with the test-value, and continue_on uses {{item}}
            assert print_message_step._build_with_param() == "test-value"
            assert (
                print_message_step.arguments
                and print_message_step.arguments[0].name == "continue_on"
                and print_message_step.arguments[0].value == "{{item}}"
            )


def test_script_arg_building_using_arguments():
    # WHEN - we use arguments to pass in a value for the "continue_on" name clashing arg
    with Workflow(generate_name="name-clash-", entrypoint="name-clash-example"):
        with Steps(name="name-clash-example"):
            print_message_step: Step = print_message(
                name="print-message", arguments=Parameter(name="continue_on", value="test-value")
            )

            # THEN - "continue_on" has the value "test-value"
            assert (
                print_message_step.arguments
                and print_message_step.arguments[0].name == "continue_on"
                and print_message_step.arguments[0].value == "test-value"
            )


@script()
def print_message_with_param(with_param: Any = {"key": "name-clash-arg"}):
    print(with_param)


@pytest.mark.parametrize(
    "with_param_value,expected_built_value",
    [
        (Parameter(name="dummy-name", value='{"serialized": "dict"}'), '{"serialized": "dict"}'),
        ({"unserialized": "dict"}, '{"unserialized": "dict"}'),
    ],
)
def test_script_arg_building_with_param_name_clash_parameter(with_param_value, expected_built_value):
    # WHEN - we have a name clash with "with_param"
    with Workflow(generate_name="with-param-name-clash-", entrypoint="name-clash-example"):
        with Steps(name="name-clash-example"):
            print_message_step: Step = print_message_with_param(name="print-message", with_param=with_param_value)

            # THEN - the "with_param" behaviour takes precedence no matter the type of with_param
            assert print_message_step._build_with_param() == expected_built_value
            assert (
                print_message_step.arguments
                and print_message_step.arguments[0].name == "with_param"
                and print_message_step.arguments[0].value == "{{item}}"
            )


@script()
def print_message_arguments(arguments: Any = {"key": "name-clash-arg"}):
    print(arguments)


@pytest.mark.parametrize(
    "arguments_value,expected_name,expected_value",
    [
        (Parameter(name="dummy-name", value='{"serialized": "dict"}'), "dummy-name", '{"serialized": "dict"}'),
        ({"unserialized": "dict"}, "unserialized", "dict"),
    ],
)
def test_script_arg_building_arguments_name_clash_parameter(arguments_value, expected_name, expected_value):
    # WHEN - we have a name clash with "arguments"
    with Workflow(generate_name="arguments-name-clash-", entrypoint="name-clash-example"):
        with Steps(name="name-clash-example"):
            print_message_step: Step = print_message_with_param(name="print-message", arguments=arguments_value)

            # THEN - the "arguments" behaviour follows usual rules for Parameters and dicts
            built_args = print_message_step._build_arguments()
            assert (
                built_args.parameters
                and built_args.parameters[0].name == expected_name
                and built_args.parameters[0].value == expected_value
            )
