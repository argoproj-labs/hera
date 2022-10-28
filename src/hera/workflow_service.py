"""Holds the workflow service that supports client workflow submissions"""
from typing import Optional, Tuple

from argo_workflows.apis import (
    CronWorkflowServiceApi,
    WorkflowServiceApi,
    WorkflowTemplateServiceApi,
)
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1CreateCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1CronWorkflow,
    IoArgoprojWorkflowV1alpha1CronWorkflowResumeRequest,
    IoArgoprojWorkflowV1alpha1CronWorkflowSuspendRequest,
    IoArgoprojWorkflowV1alpha1LintCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1UpdateCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
    IoArgoprojWorkflowV1alpha1WorkflowLintRequest,
    IoArgoprojWorkflowV1alpha1WorkflowTemplate,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateCreateRequest,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateLintRequest,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateUpdateRequest,
)

from hera.client import Client
from hera.config import Config
from hera.host_config import get_global_namespace
from hera.workflow_status import WorkflowStatus


class WorkflowService:
    """Argo workflow service for performing actions against workflows - submissions, deletions, etc.

    Parameters
    ----------
    host: Optional[str] = None
        The host of the Argo server to submit workflows to. An attempt to assemble a host from the globally set host
        (`hera.set_global_host`) is performed, followed by an attempt to get a host from Argo K8S cluster
        environment variables if this is not specified.
    verify_ssl: bool = True
        Whether to perform SSL/TLS verification. Set this to false to skip verifying SSL certificate when submitting
        workflows from an HTTPS server.
    token: Optional[str] = None
        The token to use for authentication purposes. Note that this assumes the Argo deployment is fronted with a
        deployment/service that can intercept a request and check the Bearer token. An attempt is performed to get the
        token from the global context (`hera.set_global_token`).
    namespace: Optional[str] = None
        The K8S namespace the workflow service creates workflows in. This defaults to the `default` namespace if a
        namespace is not passed or a global namespace is not set.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: bool = True,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self._host = host
        self._verify_ssl = verify_ssl
        self._namespace = get_global_namespace() if namespace is None else namespace
        self._api_client = Client(Config(host=self._host, verify_ssl=self._verify_ssl), token=token).api_client

    def create_workflow(self, workflow: IoArgoprojWorkflowV1alpha1Workflow) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Creates the given workflow to the given namespace.

        Parameters
        ----------
        workflow: IoArgoprojWorkflowV1alpha1Workflow
            The workflow to submit.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Workflow
            The submitted workflow.

        Raises
        ------
        argo.workflows.client.ApiException
        """
        return WorkflowServiceApi(api_client=self._api_client).create_workflow(
            self._namespace,
            IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=workflow, _check_type=False),
            _check_return_type=False,
        )

    def lint_workflow(self, workflow: IoArgoprojWorkflowV1alpha1Workflow) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Lints the given workflow.

        Parameters
        ----------
        workflow: IoArgoprojWorkflowV1alpha1Workflow
            Workflow to lint.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Workflow
            Linted workflow.
        """
        return WorkflowServiceApi(api_client=self._api_client).lint_workflow(
            self._namespace,
            IoArgoprojWorkflowV1alpha1WorkflowLintRequest(workflow=workflow, _check_type=False),
            _check_return_type=False,
        )

    def get_workflow(self, name: str) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Fetches a workflow by the specified name and namespace combination.

        Parameters
        ----------
        name: str
            Name of the workflow.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Workflow
        """
        return WorkflowServiceApi(api_client=self._api_client).get_workflow(
            self._namespace, name, _check_return_type=False
        )

    def get_workflow_status(self, name: str) -> WorkflowStatus:
        """Returns the workflow status of the workflow identified by the specified name.

        Parameters
        ----------
        name: str
            Name of the workflow to fetch the status of.

        Returns
        -------
        WorkflowStatus
        """
        argo_status = self.get_workflow(name).status.get("phase")
        return WorkflowStatus.from_argo_status(argo_status)

    def get_workflow_link(self, name: str) -> str:
        """Assembles a workflow link for the given workflow name.

        Parameters
        ----------
        name: str
            The name of the workflow to assemble a link for.

        Returns
        -------
        str
            The workflow link.

        Notes
        -----
        The returned path works only for Argo.
        """
        return f"{self._host}/workflows/{self._namespace}/{name}?tab=workflow"

    def delete_workflow(self, name: str) -> Tuple[object, int, dict]:
        """Deletes a workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: str
            The name of the workflow to delete.

        Returns
        -------
        Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException
        """
        return WorkflowServiceApi(api_client=self._api_client).delete_workflow(self._namespace, name)

    def lint_workflow_template(
        self, workflow: IoArgoprojWorkflowV1alpha1WorkflowTemplate
    ) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Lints the given workflow template.

        Parameters
        ----------
        workflow: IoArgoprojWorkflowV1alpha1WorkflowTemplate
            Workflow template to lint.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1WorkflowTemplate
            Linted workflow template.
        """
        return WorkflowTemplateServiceApi(api_client=self._api_client).lint_workflow_template(
            self._namespace,
            IoArgoprojWorkflowV1alpha1WorkflowTemplateLintRequest(workflow=workflow, _check_type=False),
            _check_return_type=False,
        )

    def create_workflow_template(
        self, workflow_template: IoArgoprojWorkflowV1alpha1WorkflowTemplate
    ) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Creates given workflowTemplate in the argo server.

        Parameters
        ----------
        workflow_template: V1alpha1WorkflowTemplate
            The workflowTemplate to create.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1WorkflowTemplate
            The created workflow template.

        Raises
        ------
        argo.workflows.client.ApiException
            Upon any HTTP-related errors.
        """
        return WorkflowTemplateServiceApi(api_client=self._api_client).create_workflow_template(
            self._namespace,
            IoArgoprojWorkflowV1alpha1WorkflowTemplateCreateRequest(template=workflow_template, _check_type=False),
            _check_return_type=False,
        )

    def update_workflow_template(
        self, name: str, workflow_template: IoArgoprojWorkflowV1alpha1WorkflowTemplate
    ) -> Tuple[object, int, dict]:
        """Updates a workflow template based on name and new spec.

        Parameters
        ----------
        name: str
            The name of the workflow template to update.
        workflow_template: IoArgoprojWorkflowV1alpha1WorkflowTemplate
            The new specification of the workflow template that overwrites the existing template.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1WorkflowTemplate
            The updated workflow template.
        """
        return WorkflowTemplateServiceApi(api_client=self._api_client).update_workflow_template(
            self._namespace,
            name,
            IoArgoprojWorkflowV1alpha1WorkflowTemplateUpdateRequest(template=workflow_template),
        )

    def delete_workflow_template(self, name: str) -> Tuple[object, int, dict]:
        """Deletes a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: str
            The name of the cron workflow to delete.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return WorkflowTemplateServiceApi(api_client=self._api_client).delete_workflow_template(self._namespace, name)

    def lint_cron_workflow(
        self, workflow: IoArgoprojWorkflowV1alpha1CronWorkflow
    ) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Lints the given cron workflow.

        Parameters
        ----------
        workflow: IoArgoprojWorkflowV1alpha1CronWorkflow
            Cron workflow to lint.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1CronWorkflow
            Linted cron workflow.
        """
        return CronWorkflowServiceApi(api_client=self._api_client).lint_cron_workflow(
            self._namespace,
            IoArgoprojWorkflowV1alpha1LintCronWorkflowRequest(workflow=workflow, _check_type=False),
            _check_return_type=False,
        )

    def create_cron_workflow(
        self, workflow: IoArgoprojWorkflowV1alpha1CronWorkflow
    ) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Creates given cron workflow in the argo server.

        Parameters
        ----------
        cron_workflow: V1alpha1CronWorkflow
            The cron workflow to create.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1CronWorkflow
            The created cron workflow.

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return CronWorkflowServiceApi(api_client=self._api_client).create_cron_workflow(
            self._namespace,
            IoArgoprojWorkflowV1alpha1CreateCronWorkflowRequest(cron_workflow=workflow, _check_type=False),
            _check_return_type=False,
        )

    def update_cron_workflow(
        self,
        name: str,
        cron_workflow: IoArgoprojWorkflowV1alpha1CronWorkflow,
    ) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Updates given cron workflow in the argo server.

        Parameters
        ----------
        cron_workflow: V1alpha1CronWorkflow
            The cron workflow to update.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1CronWorkflow
            The updated cron workflow.

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return CronWorkflowServiceApi(api_client=self._api_client).update_cron_workflow(
            self._namespace,
            name,
            IoArgoprojWorkflowV1alpha1UpdateCronWorkflowRequest(cron_workflow=cron_workflow, _check_type=False),
            _check_return_type=False,
        )

    def delete_cron_workflow(self, name: str) -> Tuple[object, int, dict]:
        """Deletes a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: str
            The name of the cron workflow to delete.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return CronWorkflowServiceApi(api_client=self._api_client).delete_cron_workflow(self._namespace, name)

    def get_cron_workflow(self, name: str) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Fetches a workflow by the specified name and namespace combination.

        Parameters
        ----------
        name: str
            Name of the workflow.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Workflow
        """
        return CronWorkflowServiceApi(api_client=self._api_client).get_cron_workflow(
            self._namespace, name, _check_return_type=False
        )

    def suspend_cron_workflow(self, name: str) -> Tuple[object, int, dict]:
        """Suspends a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to suspend.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return CronWorkflowServiceApi(api_client=self._api_client).suspend_cron_workflow(
            self._namespace,
            name,
            body=IoArgoprojWorkflowV1alpha1CronWorkflowSuspendRequest(name=name, namespace=self._namespace),
            _check_return_type=False,
        )

    def resume_cron_workflow(self, name: str) -> Tuple[object, int, dict]:
        """Resumes execution of a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to resume.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return CronWorkflowServiceApi(api_client=self._api_client).resume_cron_workflow(
            self._namespace,
            name,
            body=IoArgoprojWorkflowV1alpha1CronWorkflowResumeRequest(name=name, namespace=self._namespace),
            _check_return_type=False,
        )

    def get_cron_workflow_link(self, name: str) -> str:
        """Assembles a cron workflow link for the given cron workflow name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to assemble a link for.

        Returns
        -------
        str
            The cron workflow link.

        Notes
        -----
        The returned path works only for Argo.
        """
        return f"{self._host}/cron-workflows/{self._namespace}/{name}"
