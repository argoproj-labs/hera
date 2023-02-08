import json
from textwrap import dedent
from unittest import mock

import pytest
from argo_workflows.models import (
    Capabilities,
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Sequence,
    IoArgoprojWorkflowV1alpha1Template,
    SecurityContext,
)
from argo_workflows.models import Toleration as _ArgoToleration

from hera import (
    DAG,
    Artifact,
    Backoff,
    ConfigMapEnv,
    ConfigMapEnvFrom,
    ConfigMapVolume,
    ContainerPort,
    EmptyDirVolume,
    Env,
    ExistingVolume,
    GCSArtifact,
    GitArtifact,
    GPUToleration,
    Memoize,
    Metric,
    Metrics,
    Operator,
    Parameter,
    Resources,
    ResourceTemplate,
    RetryPolicy,
    RetryStrategy,
    S3Artifact,
    Sequence,
    Task,
    TaskResult,
    TaskSecurityContext,
    TemplateRef,
    Toleration,
    Volume,
    WorkflowStatus,
)


class TestTask:
    def test_next_and_shifting_set_correct_dependencies(self, no_op):
        t1, t2, t3 = Task("t1", no_op), Task("t2", no_op), Task("t3", no_op)
        t1.next(t2).next(t3)
        assert t2.depends == "t1"
        assert t3.depends == "t2"

        t4, t5, t6 = Task("t4", no_op), Task("t5", no_op), Task("t6", no_op)
        t4 >> t5 >> t6
        assert t5.depends == "t4"
        assert t6.depends == "t5"

    def test_next_does_not_set_dependency_multiple_times(self):
        t1, t2 = Task("t1"), Task("t2")
        t1 >> t2
        assert t2.depends == "t1"
        with pytest.raises(ValueError):
            # Already added
            t1 >> t2

    def test_func_and_func_param_validation_raises_on_empty_params(self, op):
        with pytest.raises(AssertionError) as e:
            Task("t", op, [])
        assert str(e.value) == "`with_param` cannot be empty"

    def test_func_and_func_param_validation_raises_on_difference(self, op):
        with pytest.raises(AssertionError) as e:
            Task("t", op, [{"a": 1}, {"b": 1}])
        assert str(e.value) == "`with_param` contains dicts with different set of keys"

    def test_param_getter_returns_empty(self, no_op):
        t = Task("t", no_op)
        assert not t.inputs

    def test_param_getter_parses_on_multi_params(self, op):
        t = Task("t", op, [{"a": 1}, {"a": 2}, {"a": 3}])
        for i in t.inputs:
            assert isinstance(i, Parameter)
            assert i.name == "a"
            assert i.value == "{{item.a}}"

    def test_param_getter_parses_single_param_val_on_json_payload(self, op):
        t = Task("t", op, [{"a": 1}])
        assert len(t.inputs) == 1
        first_input = t.inputs[0]
        assert isinstance(first_input, Parameter)
        assert first_input.name == "a"
        assert first_input.value == "{{item.a}}"

    def test_param_script_portion_adds_formatted_json_calls(self, op):
        t = Task("t", op, [{"a": 1}])
        script = t._get_param_script_portion()
        assert script == dedent(
            """\
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''
            """
        )

    def test_script_getter_returns_expected_string(self, op, typed_op):
        t = Task("t", op, [{"a": 1}])
        script = t._get_script()
        assert script == dedent(
            """\
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            print(a)
            """
        )

        t = Task("t", typed_op, [{"a": 1}])
        script = t._get_script()
        assert script == dedent(
            """\
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            print(a)
            return [{"a": (a, a)}]
            """
        )

    def test_script_getter_parses_multi_line_function(self, long_op):
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

        expected_script = dedent(
            """\
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: very_long_parameter_name = json.loads(r'''{{inputs.parameters.very_long_parameter_name}}''')
            except: very_long_parameter_name = r'''{{inputs.parameters.very_long_parameter_name}}'''
            try: very_very_long_parameter_name = json.loads(r'''{{inputs.parameters.very_very_long_parameter_name}}''')
            except: very_very_long_parameter_name = r'''{{inputs.parameters.very_very_long_parameter_name}}'''
            try: very_very_very_long_parameter_name = json.loads(r'''{{inputs.parameters.very_very_very_long_parameter_name}}''')
            except: very_very_very_long_parameter_name = r'''{{inputs.parameters.very_very_very_long_parameter_name}}'''
            try: very_very_very_very_long_parameter_name = json.loads(r'''{{inputs.parameters.very_very_very_very_long_parameter_name}}''')
            except: very_very_very_very_long_parameter_name = r'''{{inputs.parameters.very_very_very_very_long_parameter_name}}'''
            try: very_very_very_very_very_long_parameter_name = json.loads(r'''{{inputs.parameters.very_very_very_very_very_long_parameter_name}}''')
            except: very_very_very_very_very_long_parameter_name = r'''{{inputs.parameters.very_very_very_very_very_long_parameter_name}}'''

            print(42)
            """
        )
        assert t._get_script() == expected_script

    def test_resources_returned_with_appropriate_limits(self, op):
        r = Resources(cpu_request=1, memory_request="4Gi")
        t = Task("t", op, [{"a": 1}], resources=r)
        resources = t._build_script().resources

        assert resources["requests"]["cpu"] == "1"
        assert resources["requests"]["memory"] == "4Gi"

    def test_resources_returned_with_gpus(self, op):
        r = Resources(gpus=2)
        t = Task("t", op, [{"a": 1}], resources=r)
        resources = t._build_script().resources

        assert resources["requests"]["nvidia.com/gpu"] == "2"
        assert resources["limits"]["nvidia.com/gpu"] == "2"

    def test_volume_mounts_returns_expected_volumes(self, no_op):
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

    def test_container_port_returns_expected_ports(self, no_op):
        t = Task(
            "t",
            no_op,
            ports=[ContainerPort(8080, name="test-port")],
        )
        cp = t.ports
        assert cp[0].name == "test-port"
        assert cp[0].container_port == 8080

    def test_gpu_toleration_returns_expected_toleration(self):
        tn = GPUToleration
        assert tn.key == "nvidia.com/gpu"
        assert tn.effect == "NoSchedule"
        assert tn.operator == "Equal"
        assert tn.value == "present"

    def test_task_with_default_value_in_toleration(self, no_op):
        toleration = Toleration(key="nvidia.com/gpu", effect="NoSchedule", operator="Equal")
        t = Task("t", no_op, tolerations=[toleration])

        assert t.tolerations[0].value == ""
        assert t.tolerations[0].key == "nvidia.com/gpu"
        assert t.tolerations[0].effect == "NoSchedule"
        assert t.tolerations[0].operator == "Equal"

    def test_task_command_parses(self, op):
        t = Task("t", op, with_param=[{"a": 1}])
        assert t.get_command() == ["python"]

    def test_task_spec_returns_with_param(self, op):
        items = [{"a": 1}, {"a": 1}, {"a": 1}]
        t = Task("t", op, with_param=items)
        s = t._build_dag_task()

        assert s.name == "t"
        assert s.template == "t"
        assert len(s.arguments.parameters) == 1
        assert json.loads(s.with_param) == items

    def test_task_spec_returns_with_single_values(self, op):
        t = Task("t", op, [{"a": 1}])
        s = t._build_dag_task()

        assert s.name == "t"
        assert s.template == "t"
        assert len(s.arguments.parameters) == 1
        assert s.arguments.parameters[0].name == "a"
        assert s.arguments.parameters[0].value == "{{item.a}}"
        assert not hasattr(s, "with_sequence")

    def test_task_template_does_not_contain_gpu_references(self, op):
        t = Task("t", op, [{"a": 1}], resources=Resources())
        tt = t._build_template()

        assert not hasattr(tt, "tolerations")
        assert not hasattr(tt, "retry_strategy")
        assert isinstance(tt.name, str)
        assert isinstance(tt.script.source, str)
        assert isinstance(tt.inputs, IoArgoprojWorkflowV1alpha1Inputs)
        assert not hasattr(tt, "node_selector")
        assert not hasattr(tt, "timeout")

    def test_task_template_contains_expected_field_values_and_types(self, op, affinity):
        t = Task(
            "t",
            op,
            [{"a": 1}],
            resources=Resources(gpus=1),
            tolerations=[GPUToleration],
            node_selectors={"abc": "123-gpu"},
            retry_strategy=RetryStrategy(backoff=Backoff(duration="1", max_duration="2")),
            daemon=True,
            affinity=affinity,
            memoize=Memoize("a", "b", "1h"),
            timeout="5m",
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
        assert tt.script.source == dedent(
            """\
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            print(a)
            """
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
        assert hasattr(tt, "timeout")
        assert tt.timeout == "5m"

    def test_task_template_does_not_add_affinity_when_none(self, no_op):
        t = Task("t", no_op)
        tt = t._build_template()

        assert not hasattr(tt, "affinity")

    def test_task_template_contains_expected_retry_strategy(self, no_op):
        r = RetryStrategy(backoff=Backoff(duration="3", max_duration="9"))
        t = Task("t", no_op, retry_strategy=r)
        assert t.retry_strategy is not None
        assert t.retry_strategy.backoff is not None
        assert t.retry_strategy.backoff.duration == "3"
        assert t.retry_strategy.backoff.max_duration == "9"

        tt = t._build_template()
        assert tt is not None
        assert tt.retry_strategy is not None
        assert tt.retry_strategy.backoff is not None

        template_backoff = tt.retry_strategy.backoff
        retry_backoff = r.build().backoff

        assert int(template_backoff.duration) == int(retry_backoff.duration)
        assert int(template_backoff.max_duration) == int(retry_backoff.max_duration)

    def test_task_get_retry_returns_expected_none(self, no_op):
        t = Task("t", no_op)

        tt = t._build_template()
        assert hasattr(tt, "retry_strategy") is False

    def test_task_sets_kwarg(self, kwarg_op, kwarg_op_bool_default, kwarg_op_none_default, kwarg_multi_op):
        t = Task("t", kwarg_op)
        deduced_input = t.inputs[0]
        assert isinstance(deduced_input, Parameter)
        assert deduced_input.name == "a"
        assert deduced_input.default == "42"

        # Ensure defaults are json encoded. This ensures eg: `x=False` is not converted
        # into `x="False"`, which is actually truth-y.
        t = Task("t", kwarg_op_bool_default)
        deduced_input_1 = t.inputs[0]
        assert isinstance(deduced_input_1, Parameter)
        assert deduced_input_1.name == "a"
        assert deduced_input_1.value == None
        assert deduced_input_1.default == "false"

        t = Task("t", kwarg_op_bool_default, [{"a": True}])
        deduced_input_1 = t.inputs[0]
        assert isinstance(deduced_input_1, Parameter)
        assert deduced_input_1.name == "a"
        assert deduced_input_1.value == "{{item.a}}"
        assert deduced_input_1.default == "false"

        # Ensure function parameters with None defaults are distinguished from missing
        # arguments in *internal* code. This ensures eg: `x=None` is not incorrectly
        # thought to be missing an argument when creating a Task.
        t = Task("t", kwarg_op_none_default)
        deduced_input_1 = t.inputs[0]
        assert isinstance(deduced_input_1, Parameter)
        assert deduced_input_1.name == "a"
        assert deduced_input_1.value == None
        assert deduced_input_1.default == "null"

        t = Task("t", kwarg_op_none_default, [{"a": None}])
        deduced_input_1 = t.inputs[0]
        assert isinstance(deduced_input_1, Parameter)
        assert deduced_input_1.name == "a"
        assert deduced_input_1.value == "{{item.a}}"
        assert deduced_input_1.default == "null"

        t = Task("t", kwarg_multi_op, [{"a": 50}])
        deduced_input_1 = t.inputs[0]
        assert isinstance(deduced_input_1, Parameter)
        assert deduced_input_1.name == "a"
        assert deduced_input_1.value == "{{item.a}}"

        deduced_input_2 = t.inputs[1]
        assert isinstance(deduced_input_2, Parameter)
        assert deduced_input_2.name == "b"
        assert deduced_input_2.value is None
        assert deduced_input_2.default == "43"

        t = Task("t", kwarg_multi_op, [{"b": 50}])
        deduced_input_1 = t.inputs[0]
        assert isinstance(deduced_input_1, Parameter)
        assert deduced_input_1.name == "a"
        assert deduced_input_1.value is None
        assert deduced_input_1.default == "42"

        deduced_input_2 = t.inputs[1]
        assert isinstance(deduced_input_2, Parameter)
        assert deduced_input_2.name == "b"
        assert deduced_input_2.value == "{{item.b}}"

    def test_task_fails_artifact_validation(no_op, artifact):
        with pytest.raises(AssertionError) as e:
            Task("t", no_op, inputs=[artifact, artifact])
        assert str(e.value) == "input artifacts must have unique names"

    def test_task_artifact_returns_expected_list(self, no_op, artifact):
        t = Task("t", no_op, inputs=[artifact])

        artifact = t.inputs[0].as_input()
        assert artifact.name == artifact.name
        assert artifact.path == artifact.path

    def test_task_adds_s3_input_artifact(self):
        t = Task("t", inputs=[S3Artifact("n", "/p", "s3://my-bucket", "key")])

        artifact = t.inputs[0].as_input()
        assert artifact.name == "n"
        assert artifact.s3.bucket == "s3://my-bucket"
        assert artifact.s3.key == "key"

    def test_task_adds_gcs_input_artifact(self):
        t = Task("t", inputs=[GCSArtifact("n", "/p", "gs://my-bucket", "key")])

        artifact = t.inputs[0].as_input()
        assert artifact.name == "n"
        assert artifact.gcs.bucket == "gs://my-bucket"
        assert artifact.gcs.key == "key"

    def test_task_adds_git_input_artifact(self):
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
    def task_security_context_kwargs(self):
        sc_kwargs = {
            "run_as_user": 1000,
            "run_as_group": 1001,
            "run_as_non_root": False,
            "additional_capabilities": ["SYS_RAWIO"],
        }
        return sc_kwargs

    def test_task_contains_specified_security_context(self, no_op, task_security_context_kwargs):
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
    def test_task_specified_partial_security_context(self, no_op, set_only, task_security_context_kwargs):
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

    def test_task_does_not_contain_specified_security_context(self, no_op):
        t = Task("t", no_op)

        script_def = t._build_script()
        assert script_def
        assert "security_context" not in script_def

    def test_task_template_has_correct_labels(self, op):
        t = Task("t", op, [{"a": 1}], resources=Resources(), labels={"foo": "bar"})
        tt = t._build_template()
        expected_labels = {"foo": "bar"}
        assert tt.metadata.labels == expected_labels

    def test_task_template_has_correct_annotations(self, op):
        t = Task("t", op, [{"a": 1}], resources=Resources(), annotations={"foo": "bar"})
        tt = t._build_template()
        expected_annotations = {"foo": "bar"}
        assert tt.metadata.annotations == expected_annotations

    def test_task_with_config_map_env_variable(self, no_op):
        t = Task("t", no_op, env=[ConfigMapEnv(name="n", config_map_name="cn", config_map_key="k")])
        tt = t._build_template()
        assert tt.script.env[0].value_from.config_map_key_ref.name == "cn"
        assert tt.script.env[0].value_from.config_map_key_ref.key == "k"

    def test_task_with_config_map_env_from(self, no_op):
        t = Task("t", no_op, env=[ConfigMapEnvFrom(prefix="p", config_map_name="cn")])
        tt = t._build_template()
        assert tt.script.env_from[0].prefix == "p"
        assert tt.script.env_from[0].config_map_ref.name == "cn"

    def test_task_should_create_task_with_container_template(self):
        t = Task("t", command=["cowsay"], resources=Resources(memory_request="4Gi"))
        tt = t._build_template()

        assert tt.container.image == "python:3.7"
        assert tt.container.command[0] == "cowsay"
        assert tt.container.resources["requests"]["memory"] == "4Gi"

    def test_task_allow_subclassing_when_assigned_next(self, no_op):
        class SubclassTask(Task):
            pass

        t = SubclassTask("t", no_op)
        t2 = Task("t2", no_op)
        t.next(t2)
        assert t2.depends == "t"

    def test_supply_args(self):
        t = Task("t", args=["arg"])
        tt = t._build_template()
        assert tt.container.args == ["arg"]
        assert "command" not in tt.container

    def test_task_script_def_volume_template(self, no_op):
        t = Task("t", no_op, volumes=[Volume(size="1Gi", mount_path="/tmp")])

        template = t._build_script()
        assert template
        assert len(template.volume_mounts) == 1
        assert template.volume_mounts[0].mount_path == "/tmp"

    def test_task_adds_custom_resources(self, no_op):
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

    def test_task_adds_variable_as_env_var(self):
        t = Task("t")
        t1 = Task(
            "t1",
            "print(42)",
            env=[
                Env(name="id", value_from_input=t.id),
                Env(name="ip", value_from_input=t.ip),
                Env(name="status", value_from_input=t.status),
                Env(name="exit_code", value_from_input=t.exit_code),
                Env(name="started_at", value_from_input=t.started_at),
                Env(name="finished_at", value_from_input=t.finished_at),
            ],
        )
        t1s = t1._build_script()

        expected_param_name = Env._sanitise_param_for_argo("ip")
        assert t1s.env[1].name == "ip"
        assert t1s.env[1].value == f"{{{{inputs.parameters.{expected_param_name}}}}}"

        t1g = t1._build_arguments()
        assert t1g is not None
        assert len(t1g.parameters) == 6
        assert t1g.parameters[1].name == expected_param_name
        assert t1g.parameters[1].value == "{{tasks.t.ip}}"

    def test_task_adds_other_task_on_success(self):
        t = Task("t")
        o = Task("o")

        t.on_success(o)
        assert o.depends == f"t.{TaskResult.Succeeded}"

    def test_task_adds_other_task_on_failure(self):
        t = Task("t")
        o = Task("o")

        t.on_failure(o)
        assert o.depends == f"t.{TaskResult.Failed}"

    def test_task_adds_other_task_on_error(self):
        t = Task("t")
        o = Task("o")

        t.on_error(o)
        assert o.depends == f"t.{TaskResult.Errored}"

    def test_task_has_expected_retry_limit(self):
        t = Task("t", retry_strategy=RetryStrategy(limit=5))
        tt = t._build_template()
        assert tt is not None
        assert tt.retry_strategy is not None
        assert tt.retry_strategy.limit == "5"

    def test_task_has_expected_retry_policy(self):
        t = Task("t", retry_strategy=RetryStrategy(retry_policy=RetryPolicy.Always))
        tt = t._build_template()
        assert tt is not None
        assert tt.retry_strategy is not None
        assert tt.retry_strategy.retry_policy == "Always"

    def test_task_uses_expected_template_ref(self):
        t = Task("t", template_ref=TemplateRef(name="workflow-template", template="template"))._build_dag_task()
        assert hasattr(t, "template_ref")
        assert t.template_ref.name == "workflow-template"
        assert t.template_ref.template == "template"

    def test_task_does_not_include_imports_when_no_params_are_specified(self, no_op):
        t = Task("t", no_op)
        t_script = t._get_script()
        assert "import json" not in t_script
        assert "pass\n" in t_script

    def test_task_adds_exit_condition(self, no_op):
        t = Task("t", no_op)
        t.on_workflow_status(WorkflowStatus.Succeeded)
        assert t.when == "{{workflow.status}} == Succeeded"

    def test_all_failed_adds_dependency(self, no_op, multi_op):
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

    def test_any_succeeded_adds_dependency(self, no_op, multi_op):
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

    def test_task_fails_to_validate_with_incorrect_memoize(self, op):
        with pytest.raises(AssertionError) as e:
            Task("t", op, with_param=[{"a": 42}], memoize=Memoize("b", "a", "a-key"))
        assert str(e.value) == "memoize key must be a parameter of the function"

    def test_task_template_contains_resource_template(self):
        resource_template = ResourceTemplate(action="create")
        t = Task(name="t", resource_template=resource_template)
        tt = t._build_template()
        resource = resource_template.build()
        assert tt.resource == resource

    def test_task_template_with_resource_template_has_no_container(self):
        resource_template = ResourceTemplate(action="create")
        t = Task(name="t", resource_template=resource_template)
        tt = t._build_template()
        assert not hasattr(tt, "container")

    def test_task_init_raises_on_incorrect_kwargs(self, no_op):
        with pytest.raises(ValueError) as e:
            Task("t", source=no_op, dag=DAG("d"))
        assert str(e.value) == "Cannot use both `dag` and `source`"

        with pytest.raises(ValueError) as e:
            Task("t", dag=DAG("d"), template_ref=TemplateRef(template="tref", name="abc"))
        assert str(e.value) == "Cannot use both `dag` and `template_ref`"

        with pytest.raises(ValueError) as e:
            Task("t", with_param=["abc"], with_sequence=Sequence("abc"))
        assert str(e.value) == "Cannot use both `with_sequence` and `with_param`"

    def test_task_uses_sequences(self):
        t = Task("t", with_sequence=Sequence("abc", start=1, end=42))._build_dag_task()
        assert isinstance(t, IoArgoprojWorkflowV1alpha1DAGTask)
        assert hasattr(t, "with_sequence")
        assert isinstance(t.with_sequence, IoArgoprojWorkflowV1alpha1Sequence)
        assert hasattr(t.with_sequence, "start")
        assert hasattr(t.with_sequence, "end")
        assert hasattr(t.with_sequence, "format")
        assert t.with_sequence.start == "1"
        assert t.with_sequence.end == "42"
        assert t.with_sequence.format == "abc"

    def test_task_utilize_items(self, no_op):
        error_string = "`with_param` or `with_sequence` items are utilized in inputs, nor could they be deduced"
        with pytest.raises(ValueError) as e:
            Task("t", no_op, with_sequence=Sequence("abc", start=1, end=42))
        assert str(e.value) == error_string
        with pytest.raises(ValueError) as e:
            Task("t", no_op, with_param=[1, 2, 3])
        assert str(e.value) == error_string

    def test_get_dependency_tasks_returns_None_on_no_depends(self):
        t = Task("t")
        t.depends = None  # explicit setting
        deps = t._get_dependency_tasks()
        assert deps == []

    def test_rrshift(self):
        with pytest.raises(AssertionError) as e:
            Task("t").__rrshift__(42)  # type: ignore
        assert "Unknown type" in str(e.value)
        assert "specified using reverse right bitshift operator" in str(e.value)

        a, b, c = Task("a"), Task("b"), Task("c")
        [a, b] >> c
        assert a.depends is None
        assert b.depends is None
        assert c.depends is not None

    def test_rshift(self):
        with pytest.raises(AssertionError) as e:
            Task("t") >> [42]  # type: ignore
        assert "Unknown list item type" in str(e.value)
        assert "specified using right bitshift operator `>>`" in str(e.value)

        with pytest.raises(ValueError) as e:
            Task("t") >> 42  # type: ignore
        assert "Unknown type" in str(e.value)

        a, b, c = Task("a"), Task("b"), Task("c")
        a >> [b, c]
        assert "a" in b.depends
        assert "a" in c.depends

    def test_on_workflow_status(self):
        t = Task("t")
        t.when = "42"
        t.on_workflow_status(WorkflowStatus.Succeeded)
        assert t.when == "42 && {{workflow.status}} == Succeeded"

    def test_on_other_result(self):
        a = Task("a")
        b = Task("b")
        a.on_other_result(b, "42")
        assert a.when == "'{{tasks.b.outputs.result}}' == 42"
        assert "b" in a.depends
        c = Task("c")
        a.on_other_result(c, "43")
        assert a.when == "'{{tasks.b.outputs.result}}' == 42 && '{{tasks.c.outputs.result}}' == 43"
        assert "c" in a.depends

    def test_validate(self):
        with pytest.raises(AssertionError) as e:
            Task("t", with_sequence=42).validate()  # type: ignore
        assert str(e.value) == "Accepted type for `with_sequence` is `Sequence`"

        with pytest.raises(ValueError) as e:
            Task("t", pod_spec_patch=42).validate()  # type: ignore
        assert str(e.value) == "`pod_spec_patch` must be `str` to handle argo expressions properly"

        assert Task("t", pod_spec_patch="abc").validate() is None

    def test_build_arguments(self):
        args = Task("t", inputs=[Parameter("a", value="42"), GCSArtifact("a", "b", "c", "d")])._build_arguments()
        assert isinstance(args, IoArgoprojWorkflowV1alpha1Arguments)
        assert hasattr(args, "parameters")
        assert len(args.parameters) == 1
        assert hasattr(args, "artifacts")
        assert len(args.artifacts) == 1

        args = Task("t", inputs=[Parameter("a", value="42")])._build_arguments()
        assert isinstance(args, IoArgoprojWorkflowV1alpha1Arguments)
        assert hasattr(args, "parameters")
        assert len(args.parameters) == 1
        assert not hasattr(args, "artifacts")

        args = Task("t", inputs=[GCSArtifact("a", "b", "c", "d")])._build_arguments()
        assert isinstance(args, IoArgoprojWorkflowV1alpha1Arguments)
        assert not hasattr(args, "parameters")
        assert hasattr(args, "artifacts")
        assert len(args.artifacts) == 1

        assert Task("t")._build_arguments() is None

        args = Task("t", inputs={"a": 1, "b": "abc", "c": {"d": "test"}})._build_arguments()
        assert isinstance(args, IoArgoprojWorkflowV1alpha1Arguments)
        assert hasattr(args, "parameters")
        assert len(args.parameters) == 3
        assert args.parameters[0].name == "a"
        assert args.parameters[0].value == json.dumps(1)
        assert args.parameters[1].name == "b"
        assert args.parameters[1].value == "abc"
        assert args.parameters[2].name == "c"
        assert args.parameters[2].value == json.dumps({"d": "test"})

        args = Task(
            "t",
            inputs=[
                {"a": 1, "b": "abc", "c": {"d": "test"}},
                Parameter("e", value="test"),
                GCSArtifact("a", "b", "c", "d"),
            ],
        )._build_arguments()
        assert isinstance(args, IoArgoprojWorkflowV1alpha1Arguments)
        assert hasattr(args, "parameters")
        assert len(args.parameters) == 4
        assert hasattr(args, "artifacts")
        assert len(args.artifacts) == 1
        assert args.parameters[0].name == "a"
        assert args.parameters[0].value == json.dumps(1)
        assert args.parameters[1].name == "b"
        assert args.parameters[1].value == "abc"
        assert args.parameters[2].name == "c"
        assert args.parameters[2].value == json.dumps({"d": "test"})
        assert args.parameters[3].name == "e"
        assert args.parameters[3].value == "test"
        assert args.artifacts[0].name == "a"

    def test_get_parameter(self):
        param = Task("t", outputs=[Parameter("a", value="42", default="43")]).get_parameter("a")
        assert isinstance(param, Parameter)
        assert param.name == "a"
        assert param.value == f"{{{{tasks.t.outputs.parameters.a}}}}"
        assert param.default == "43"

        with pytest.raises(KeyError) as e:
            Task("t").get_parameter("a")
        assert str(e.value) == "'No output parameter named `a` found'"

    def test_get_parameters_as(self):
        p = Task("t").get_parameters_as("a")
        assert isinstance(p, Parameter)
        assert p.name == "a"
        assert p.value == "{{tasks.t.outputs.parameters}}"

    def test_get_artifact(self):
        arti = Task("t", outputs=[GCSArtifact("a", "b", "c", "d")]).get_artifact("a")
        assert isinstance(arti, Artifact)
        assert arti.name == "a"
        assert arti.path == "b"
        assert arti.from_task == "{{tasks.t.outputs.artifacts.a}}"

        with pytest.raises(KeyError) as e:
            Task("t").get_artifact("a")
        assert str(e.value) == "'No output artifact named `a` found'"

    def test_get_result(self):
        assert Task("t").get_result() == "{{tasks.t.outputs.result}}"

    def test_get_output_condition(self):
        assert Task("t").get_output_condition(Operator.Equals, "42") == "{{tasks.t.outputs.result}} == 42"

    def test_get_result_as(self):
        p = Task("t").get_result_as("a")
        assert isinstance(p, Parameter)
        assert p.name == "a"
        assert p.value == "{{tasks.t.outputs.result}}"

    def test_deduce_input_params(self):
        params = Task("t", dag=DAG("d"))._deduce_input_params()
        assert len(params) == 0

        params = Task("t", dag=DAG("d", inputs=[Parameter("a", value="42")]))._deduce_input_params()
        assert len(params) == 1
        assert params[0].name == "a"
        assert params[0].value == "{{item}}"

        params = Task(
            "t", dag=DAG("d", inputs=[Parameter("a", value="42"), Parameter("b", value="43")])
        )._deduce_input_params()
        assert len(params) == 2
        assert params[0].name == "a"
        assert params[0].value == "{{item.a}}"
        assert params[1].name == "b"
        assert params[1].value == "{{item.b}}"

    def test_template_contains_metrics(self):
        t = Task(
            "t",
            metrics=Metrics(
                [
                    Metric(
                        'a',
                        'b',
                    ),
                    Metric(
                        'c',
                        'd',
                    ),
                ]
            ),
        )._build_template()
        assert isinstance(t, IoArgoprojWorkflowV1alpha1Template)
        assert hasattr(t, 'metrics')

    def test_task_adjusts_input_metrics(self):
        t = Task('t', metrics=Metric('a', 'b'))
        assert isinstance(t.metrics, Metrics)

        t = Task('t', metrics=[Metric('a', 'b')])
        assert isinstance(t.metrics, Metrics)

        t = Task('t', metrics=Metrics([Metric('a', 'b')]))
        assert isinstance(t.metrics, Metrics)

    def test_task_applies_hooks(self, global_config):
        def hook1(t: Task) -> None:
            t.when = "test123"

        def hook2(t: Task) -> None:
            t.labels = {'abc': '123'}

        global_config.task_post_init_hooks = [hook1, hook2]
        t = Task('test')
        assert t.when == "test123"
        assert t.labels == {'abc': '123'}

    def test_task_applies_exit(self, no_op):
        with pytest.raises(ValueError) as e:
            Task('t', source=no_op).on_exit(Task('e', dag=DAG('d')))
        assert (
            str(e.value)
            == "Provided `Task` contains a `DAG` set. Only `Task`s with `source` are supported or pure `DAG`s. "
            "Try passing in `Task.dag` or set `source` on `Task` if you have a single task to run on exit."
        )

        o = Task('e', source=no_op)
        t = Task('t', source=no_op).on_exit(o)
        assert o.is_exit_task
        assert t.exit_task == "e"

        d = DAG('d')
        t = Task('t', source=no_op).on_exit(d)
        assert t.exit_task == "d"

        o = 42
        with pytest.raises(ValueError) as e:
            Task('t', source=no_op).on_exit(o)  # type: ignore
        assert str(e.value) == f"Unrecognized exit type {type(o)}, supported types are `Task` and `DAG`"

    def test_task_properties(self):
        t = Task('t')
        assert t.id == "{{tasks.t.id}}"
        assert t.ip == "{{tasks.t.ip}}"
        assert t.status == "{{tasks.t.status}}"
        assert t.exit_code == "{{tasks.t.exitCode}}"
        assert t.started_at == "{{tasks.t.startedAt}}"
        assert t.finished_at == "{{tasks.t.finishedAt}}"
