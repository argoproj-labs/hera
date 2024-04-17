from hera.workflows import Parameter, Script, WorkflowTemplate


def foo(v):
    print(v)


with WorkflowTemplate(
    generate_name="global-parameters-", entrypoint="s", arguments=Parameter(name="v", value="42")
) as w:
    Script(name="s", source=foo, inputs=[w.get_parameter("v")])
