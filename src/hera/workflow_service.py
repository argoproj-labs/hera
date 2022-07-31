"""Holds the workflow service that supports client workflow submissions"""
from typing import Optional, Tuple

from argo_workflows.apis import WorkflowServiceApi
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
)

from hera.client import Client
from hera.config import Config
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
    namespace: str = 'default'
        The K8S namespace the cron workflow service creates cron workflows in.
        This defaults to the `default` namespace.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: bool = True,
        token: Optional[str] = None,
        namespace: str = "default",
    ):
        self._namespace = namespace
        self._config = Config(host=host, verify_ssl=verify_ssl)
        api_client = Client(self._config, token=token).api_client
        self.service = WorkflowServiceApi(api_client=api_client)

    def create(
        self,
        workflow: IoArgoprojWorkflowV1alpha1Workflow,
    ) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Creates the given workflow to the given namespace.

        Parameters
        ----------
        workflow: V1alpha1Workflow
            The workflow to submit.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Workflow
            The submitted workflow.

        Raises
        ------
        argo.workflows.client.ApiException
        """
        return self.service.create_workflow(
            self._namespace,
            IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=workflow, _check_type=False),
            _check_return_type=False,
        )

    def delete(self, name: str) -> Tuple[object, int, dict]:
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
        return self.service.delete_workflow(self._namespace, name)

    def get_workflow_link(self, name: str) -> str:
        """Assembles a workflow link for the given workflow name. Note that the returned path works only for Argo.

        Parameters
        ----------
        name: str
            The name of the workflow to assemble a link for.

        Returns
        -------
        str
            The workflow link.
        """
        return f"{self._config.host}/workflows/{self._namespace}/{name}?tab=workflow"

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
        return self.service.get_workflow(self._namespace, name, _check_return_type=False)

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
