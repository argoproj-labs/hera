import re

import pytest

from hera.workflows import Parameter, Workflow
from hera.workflows._mixins import (
    ContainerMixin,
    IOMixin,
    TemplateMixin,
    VolumeMixin,
    VolumeMountMixin,
)
from hera.workflows.artifact import Artifact
from hera.workflows.container import Container
from hera.workflows.models import (
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    Container as ModelContainer,
    EmptyDirVolumeSource,
    ImagePullPolicy,
    Inputs as ModelInputs,
    IntOrString,
    ObjectMeta,
    Outputs as ModelOutputs,
    Parameter as ModelParameter,
    PersistentVolumeClaim as ModelPersistentVolumeClaim,
    PersistentVolumeClaimSpec,
    PersistentVolumeClaimVolumeSource,
    Quantity,
    RetryStrategy as ModelRetryStrategy,
    Template as ModelTemplate,
    Volume as ModelVolume,
    VolumeMount,
    VolumeResourceRequirements,
    Workflow as ModelWorkflow,
)
from hera.workflows.retry_strategy import RetryStrategy
from hera.workflows.task import Task
from hera.workflows.volume import ExistingVolume, Volume


class TestContainerMixin:
    def test_build_image_pull_policy(self) -> None:
        assert ContainerMixin(image_pull_policy="Always")._build_image_pull_policy() == ImagePullPolicy.always.value
        assert (
            ContainerMixin(image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy()
            == ImagePullPolicy.always.value
        )
        assert ContainerMixin()._build_image_pull_policy() is None


class TestTemplateMixin:
    def test_build_retry_strategy(self):
        # None
        assert TemplateMixin(retry_strategy=None)._build_retry_strategy() is None

        # Model class
        assert TemplateMixin(
            retry_strategy=ModelRetryStrategy(limit=IntOrString(__root__=2))
        )._build_retry_strategy() == ModelRetryStrategy(limit=IntOrString(__root__=2))

        # Hera class
        assert TemplateMixin(retry_strategy=RetryStrategy(limit=2))._build_retry_strategy() == ModelRetryStrategy(
            limit=IntOrString(__root__=2)
        )


class TestIOMixin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.io_mixin = IOMixin()

    def test_get_parameter_success(self):
        self.io_mixin.inputs = Parameter(name="test", value="value")
        param = self.io_mixin.get_parameter("test")
        assert param.name == "test"
        assert param.value == "{{inputs.parameters.test}}"

    def test_get_model_parameter_success(self):
        self.io_mixin.inputs = ModelParameter(name="test", value="value")
        param = self.io_mixin.get_parameter("test")
        assert param.name == "test"
        assert param.value == "{{inputs.parameters.test}}"

    def test_get_parameter_no_inputs(self):
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("test")

    def test_get_parameter_no_parameters(self):
        self.io_mixin.inputs = ModelInputs()
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("test")

    def test_get_parameter_not_found(self):
        self.io_mixin.inputs = Parameter(name="test", value="value")
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("not_exist")

    def test_get_artifact_success(self):
        self.io_mixin.inputs = ModelInputs(artifacts=[ModelArtifact(name="test")])
        artifact = self.io_mixin.get_artifact("test")
        assert artifact.name == "test"
        assert artifact.from_ == "{{inputs.artifacts.test}}"

    def test_get_artifact_no_inputs(self):
        with pytest.raises(KeyError):
            self.io_mixin.get_artifact("test")

    def test_get_artifact_no_artifacts(self):
        self.io_mixin.inputs = ModelInputs()
        with pytest.raises(KeyError):
            self.io_mixin.get_artifact("test")

    def test_get_artifact_not_found(self):
        self.io_mixin.inputs = ModelInputs(artifacts=[ModelArtifact(name="test")])
        with pytest.raises(KeyError):
            self.io_mixin.get_artifact("not_exist")

    def test_build_inputs_none(self):
        assert self.io_mixin._build_inputs() is None

    def test_build_inputs_from_model_inputs_with_hera_parameter(self):
        self.io_mixin.inputs = ModelInputs(parameters=[ModelParameter(name="test", value="value")])
        assert self.io_mixin._build_inputs() == ModelInputs(parameters=[ModelParameter(name="test", value="value")])

    def test_build_outputs_none(self):
        assert self.io_mixin._build_outputs() is None

    def test_build_outputs_artifact_success(self):
        self.io_mixin.outputs = ModelOutputs(artifacts=[ModelArtifact(name="test")])
        built_outputs = self.io_mixin._build_outputs()
        assert built_outputs and built_outputs.artifacts == [ModelArtifact(name="test")]


class TestArgumentsMixin:
    def test_build_workflow(self):
        with Workflow(
            name="test",
            arguments=ModelArguments(parameters=[ModelParameter(name="test", value="value")]),
        ) as w:
            pass

        workflow = w.build()
        assert isinstance(workflow, ModelWorkflow)
        assert (
            workflow.spec
            and workflow.spec.arguments
            and workflow.spec.arguments.parameters == [ModelParameter(name="test", value="value")]
        )


class TestVolumeMixin:
    def test_volume_creates_pvc(self):
        # Hera `Volume` is used to create PVCs more easily, ignoring the volume itself (in _build_volumes).
        volume_mixin = VolumeMixin(
            volumes=[
                Volume(name="test-auto-PVC", mount_path="/here", size="1Mi"),
            ]
        )
        assert volume_mixin._build_volumes() is None

        assert volume_mixin._build_persistent_volume_claims() == [
            ModelPersistentVolumeClaim(
                metadata=ObjectMeta(name="test-auto-PVC"),
                spec=PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=VolumeResourceRequirements(requests={"storage": Quantity(__root__="1Mi")}),
                ),
            )
        ]

    def test_existing_volume(self):
        # ExistingVolume is converted into a ModelVolume by _build_volumes, and has no PVC generated
        volume_mixin = VolumeMixin(
            volumes=[
                ExistingVolume(name="test-existing", mount_path="/here", claim_name="some-existing-vol"),
            ]
        )
        assert volume_mixin._build_volumes() == [
            ModelVolume(
                name="test-existing",
                persistent_volume_claim=PersistentVolumeClaimVolumeSource(claim_name="some-existing-vol"),
            )
        ]

        assert volume_mixin._build_persistent_volume_claims() is None


class TestVolumeMountMixin:
    def test_volume_generates_mount(self):
        # _build_volume_mounts is a member of VolumeMountMixin (not VolumeMixin), so that Workflows can
        # use VolumeMixin to create PVCs or specify volume sources (but never mount volumes). Containers/scripts
        # use VolumeMountMixin to create PVCs, mount volumes to the container, or specify volume sources.
        volume_mixin = VolumeMountMixin(
            volumes=[
                Volume(name="test-auto-mount", mount_path="/here", size="1Mi"),
            ]
        )

        assert volume_mixin._build_volumes() is None
        assert volume_mixin._build_persistent_volume_claims() == [
            ModelPersistentVolumeClaim(
                metadata=ObjectMeta(name="test-auto-mount"),
                spec=PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=VolumeResourceRequirements(requests={"storage": Quantity(__root__="1Mi")}),
                ),
            )
        ]

        # Ensure it generates a mount automatically
        assert volume_mixin._build_volume_mounts() == [VolumeMount(name="test-auto-mount", mount_path="/here")]

    def test_volume_with_duplicated_volume_mount(self):
        # Specifying the same `VolumeMount` as would be generated by the `Volume` results in a
        # duplicate in the list of volume mounts. This is not by design and we can implement a
        # de-duplication (by `name`) enhancement if desired.
        volume_mixin = VolumeMountMixin(
            volumes=[
                Volume(name="test-auto-mount", mount_path="/here", size="1Mi"),
            ],
            volume_mounts=[VolumeMount(name="test-auto-mount", mount_path="/here")],
        )

        assert volume_mixin._build_volumes() is None
        assert volume_mixin._build_volume_mounts() == [
            VolumeMount(name="test-auto-mount", mount_path="/here"),
            VolumeMount(name="test-auto-mount", mount_path="/here"),
        ]

    def test_model_volume_and_volume_mount(self):
        # Use model classes to skip Hera's preprocessing magic
        volume_mixin = VolumeMountMixin(
            volume_mounts=[VolumeMount(name="v1", mount_path="/mnt/vol")],
            volumes=[ModelVolume(name="v1", empty_dir=EmptyDirVolumeSource())],
        )

        assert volume_mixin._build_volumes() == [ModelVolume(name="v1", empty_dir=EmptyDirVolumeSource())]
        assert volume_mixin._build_persistent_volume_claims() is None
        assert volume_mixin._build_volume_mounts() == [VolumeMount(name="v1", mount_path="/mnt/vol")]

    def test_volume_nothing_to_mount(self):
        volume_mixin = VolumeMountMixin(volumes=[ModelVolume(name="v1", empty_dir=EmptyDirVolumeSource())])

        assert volume_mixin._build_volumes() == [ModelVolume(name="v1", empty_dir=EmptyDirVolumeSource())]
        assert volume_mixin._build_volume_mounts() is None


class TestTemplateInvocatorSubNodeMixin:
    def test_get_outputs_str_template(self):
        task = Task(name="test", template="dummy")

        with pytest.raises(ValueError, match="Cannot get outputs when the template was set via a name: dummy"):
            task.get_outputs_as_arguments()

    def test_get_outputs_inline_template(self):
        task = Task(name="test", inline=Container(name="c"))

        with pytest.raises(ValueError, match=re.escape("Only 'template' is supported (not inline or template_ref)")):
            task.get_outputs_as_arguments()

    def test_get_outputs_no_outputs(self):
        container = Container(name="c")
        task = Task(name="test", template=container)

        with pytest.raises(ValueError, match="Template 'c' has no outputs"):
            task.get_outputs_as_arguments()

    def test_get_outputs_no_outputs_model_template(self):
        model_template = ModelTemplate(name="c", container=ModelContainer(image="test-image"))
        task = Task(name="test", template=model_template)

        with pytest.raises(ValueError, match="Template 'c' has no outputs"):
            task.get_outputs_as_arguments()

    def test_get_outputs_model_template_outputs_not_none(self):
        """Edge case of using a model template with a non-none `outputs`, but contains `None` for parameters and artifacts."""
        model_template = ModelTemplate(name="c", container=ModelContainer(image="test-image"), outputs=ModelOutputs())
        task = Task(name="test", template=model_template)

        with pytest.raises(ValueError, match="Template 'c' has no outputs"):
            task.get_outputs_as_arguments()

    def test_get_outputs_containing_parameter(self):
        container = Container(name="c", outputs=[ModelParameter(name="p", value="42")])
        task = Task(name="test", template=container)

        assert task.get_outputs_as_arguments() == [Parameter(name="p", value="{{tasks.test.outputs.parameters.p}}")]

    def test_get_outputs_containing_artifact(self):
        container = Container(name="c", outputs=[ModelArtifact(name="art", from_="somewhere")])
        task = Task(name="test", template=container)

        assert task.get_outputs_as_arguments() == [Artifact(name="art", from_="{{tasks.test.outputs.artifacts.art}}")]

    def test_get_outputs_containing_both(self):
        container = Container(
            name="c",
            outputs=[ModelParameter(name="p", value="42"), ModelArtifact(name="art", from_="somewhere")],
        )
        task = Task(name="test", template=container)

        assert task.get_outputs_as_arguments() == [
            Parameter(name="p", value="{{tasks.test.outputs.parameters.p}}"),
            Artifact(name="art", from_="{{tasks.test.outputs.artifacts.art}}"),
        ]

    def test_get_parameter_str_template(self):
        task = Task(name="test", template="dummy")

        with pytest.raises(
            ValueError, match="Cannot get output parameters when the template was set via a name: dummy"
        ):
            task.get_parameter("a-param")

    def test_get_parameter_inline_template(self):
        task = Task(name="test", inline=Container(name="c"))

        with pytest.raises(ValueError, match=re.escape("Only 'template' is supported (not inline or template_ref)")):
            task.get_parameter("a-param")

    def test_get_parameter_no_outputs(self):
        container = Container(name="c")
        task = Task(name="test", template=container)

        with pytest.raises(ValueError, match="Cannot get output parameters. Template 'c' has no outputs"):
            task.get_parameter("a-param")

    def test_get_parameter_no_parameters(self):
        container = Container(name="c", outputs=ModelArtifact(name="art", from_="somewhere"))
        task = Task(name="test", template=container)

        with pytest.raises(ValueError, match="Cannot get output parameters. Template 'c' has no output parameters"):
            task.get_parameter("a-param")

    def test_get_artifact_str_template(self):
        task = Task(name="test", template="dummy")

        with pytest.raises(
            ValueError, match="Cannot get output artifacts when the template was set via a name: dummy"
        ):
            task.get_artifact("an-artifact")

    def test_get_artifact_inline_template(self):
        task = Task(name="test", inline=Container(name="c"))

        with pytest.raises(ValueError, match=re.escape("Only 'template' is supported (not inline or template_ref)")):
            task.get_artifact("a-param")

    def test_get_artifact_no_outputs(self):
        container = Container(name="c")
        task = Task(name="test", template=container)

        with pytest.raises(ValueError, match="Cannot get output artifacts. Template 'c' has no outputs"):
            task.get_artifact("an-artifact")

    def test_get_artifact_no_artifacts(self):
        container = Container(
            name="c",
            outputs=[
                ModelParameter(name="p", value="42"),
            ],
        )
        task = Task(name="test", template=container)

        with pytest.raises(ValueError, match="Cannot get output artifacts. Template 'c' has no output artifacts"):
            task.get_artifact("an-artifact")
