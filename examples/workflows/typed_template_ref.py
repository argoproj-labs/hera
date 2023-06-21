from pathlib import Path
from hera.shared._base_model import BaseModel
from hera.workflows import Artifact, DAG, Container, Parameter, Script, Task, Workflow, WorkflowTemplate, script
from hera.workflows.models import TemplateRef, ValueFrom
from typing import Annotated, Optional, List, Any


# How can we avoid the duplication of "an_int" in the inputs for its enum?
# What about descriptions? Do Artifacts need improvement?
@script(inputs=[Parameter(name="an_int", enum=[1, 2, 3]), Artifact(name="my-art", from_="/tmp/path")])
def echo(message: str, a_dict: dict, an_int: int = 1):
    print(message)
    print(a_dict)
    print(an_int)
    with open("/tmp/path", "r") as f:
        print(f.readlines())


# Use typing.Annotated!
# "Parameters" are reused in the Argo spec/repo in places where it would be
# better to have separate types for "InputParameter", "InputArgument", "OutputParameter" etc

# e.g. "global_name" for an input parameter doesn't make sense

# For arguments, they will just need a name and value (I don't think value_from is
# applicable for args?)

#   default      -> Not applicable for arguments
#   description  -> Not applicable for arguments
#   enum         -> Not applicable for arguments, or output parameters
#   global_name  -> Not applicable for inputs and arguments?
#   name         -> Required for all
#   value        -> Not generally applicable for parameters?
#   value_from   -> Not applicable for arguments


class InputParameter(BaseModel):
    default: Optional[Any]
    description: Optional[str]
    enum: Optional[List[Any]]
    global_name: Optional[str]
    name: str
    value_from: Optional[ValueFrom]


class OutputParameter(BaseModel):
    default: Optional[Any]
    description: Optional[str]
    enum: Optional[List[Any]]
    global_name: Optional[str]
    name: str
    value_from: Optional[ValueFrom]


class InputArtifact(BaseModel):
    path: str

    def read_text(self) -> str:
        return Path(self.path).read_text()


# Artifacts could be improved to be args to the function, and add access contents easily?
@script()
def an_artifact(my_art: InputArtifact(path="/path")):
    my_art_text = my_art.read_text()


# vs current
@script(inputs=Artifact(name="my_art", path="/path"))
# name is actually unused!
def an_artifact():
    # We have to repeat path string unless defined outside of the function
    my_art_text = Path("/path").read_text()


@script(
    inputs=[Parameter(name="an_int", enum=[1, 2, 3])],
    outputs=[OutputParameter(name="an-output", value_from="/path")],
)
def annotated_echo(
    message: Annotated[
        str,
        InputParameter(description="A message to echo to stdout"),
    ],
    a_dict: dict,
    an_int: Annotated[int, InputParameter(enum=[1, 2, 3])] = 1,
):
    print(message)
    print(a_dict)
    print(an_int)

    with open("/path", "w") as f:
        f.write("some content for the file!")


with WorkflowTemplate(name="example-workflow-template") as wt:
    Container(
        name="cowsay",
        image="docker/whalesay",
        command=["cowsay", "{{inputs.parameters.cowsay_message}}"],
        inputs=[Parameter(name="cowsay_message")],
    )
    Script(name="echo", source=echo)

# From this WorkflowTemplate, how can we generate stubs for TemplateRefs like below?

for t in wt.templates:
    print(t)
    # ... generate stubs


class CowsayTemplateRef(TemplateRef):
    cowsay_message: str  # no indication that message is a string in the container template - str can be default due to it being yaml?
    # comes from [t._build_inputs() for t in wt.templates]

    def as_template_ref(self) -> TemplateRef:
        return wt.get_template_ref("cowsay")  # comes from [t.name for t in wt.templates]

    def get_arguments(self) -> dict:
        return self.dict(exclude=set(TemplateRef.__fields__))


class EchoTemplateRef(TemplateRef):
    message: str  # can possibly get from the function signature? Not available via template.inputs, only template._build_inputs()
    # Something like
    # [_get_parameters_from_callable(t.source) for t in wt.templates if isinstance(t, Script)]
    # We can use a modified _get_parameters_from_callable to keep the type information

    a_dict: dict
    an_int: Optional[int]

    def as_template_ref(self) -> TemplateRef:
        return wt.get_template_ref("echo")

    def get_arguments(self) -> dict:
        # Is this robust to exclude optionals? e.g. an_int if not given a value (but has a default in the workflowtemplate?)
        args = {k: v for k, v in self.dict(exclude=set(TemplateRef.__fields__)).items() if v is not None}
        return args


cowsay_ref = CowsayTemplateRef(cowsay_message="hello container!")
echo_ref = EchoTemplateRef(message="hello script!", a_dict={"test_key": "a value!"})

with Workflow(generate_name="using-a-typed-template-ref") as w:
    with DAG(name="d"):
        Task(name="cowsay-task", template_ref=cowsay_ref.as_template_ref(), arguments=cowsay_ref.get_arguments())
        Task(name="echo-task", template_ref=echo_ref.as_template_ref(), arguments=echo_ref.get_arguments())
