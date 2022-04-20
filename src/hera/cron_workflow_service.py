"""Holds the cron workflow service that supports client cron workflow creations"""
from typing import Optional, Tuple

from argo_workflows.apis import CronWorkflowServiceApi
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1CreateCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1CronWorkflow,
    IoArgoprojWorkflowV1alpha1UpdateCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1WorkflowResumeRequest,
    IoArgoprojWorkflowV1alpha1WorkflowSuspendRequest,
)

from hera.client import Client
from hera.config import Config


class CronWorkflowService:
    """Argo cron workflow service for performing actions against cron workflows - creations, deletions, etc.

    Parameters
    ----------
    host: Optional[str] = None
        The host of the Argo server to submit workflows to. An attempt to assemble a host from Argo K8S cluster
        environment variables is pursued if this is not specified.
    verify_ssl: bool = True
        Whether to perform SSL/TLS verification. Set this to false to skip verifying SSL certificate when submitting
        workflows from an HTTPS server.
    token: Optional[str] = None
        The token to use for authentication purposes. Note that this assumes the Argo deployment is fronted with a
        deployment/service that can intercept a request and check the Bearer token.
    namespace: str = 'default'
        The K8S namespace the cron workflow service creates cron workflows in.
        This defaults to the `default` namespace.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: bool = True,
        token: Optional[str] = None,
        namespace: str = 'default',
    ):
        self._host = host
        self._verify_ssl = verify_ssl
        self._namespace = namespace
        api_client = Client(Config(host=self._host, verify_ssl=self._verify_ssl), token).api_client
        self.service = CronWorkflowServiceApi(api_client=api_client)

    def create(
        self, cron_workflow: IoArgoprojWorkflowV1alpha1CronWorkflow, namespace: str = 'default'
    ) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Creates given cron workflow in the argo server.

        Parameters
        ----------
        cron_workflow: V1alpha1CronWorkflow
            The cron workflow to create.
        namespace: str = 'default'
            The K8S namespace of the Argo server to create the cron workflow in.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1CronWorkflow
            The created cron workflow.

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.create_cron_workflow(
            namespace,
            IoArgoprojWorkflowV1alpha1CreateCronWorkflowRequest(cron_workflow=cron_workflow, _check_type=False),
            _check_return_type=False,
        )

    def update(
        self,
        cron_workflow: IoArgoprojWorkflowV1alpha1CronWorkflow,
        name: str,
        namespace: str = 'default',
    ) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Updates given cron workflow in the argo server.

        Parameters
        ----------
        cron_workflow: V1alpha1CronWorkflow
            The cron workflow to update.
        namespace: str = 'default'
            The K8S namespace of the Argo server to update the cron workflow in.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1CronWorkflow
            The updated cron workflow.

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.update_cron_workflow(
            namespace,
            name,
            IoArgoprojWorkflowV1alpha1UpdateCronWorkflowRequest(cron_workflow=cron_workflow, _check_type=False),
            _check_return_type=False,
        )

    def delete(self, name: str, namespace: str = 'default') -> Tuple[object, int, dict]:
        """Deletes a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: str
            The name of the cron workflow to delete.
        namespace: str = 'default'
            The K8S namespace of the Argo server to delete the cron workflow from.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.delete_cron_workflow(namespace, name)

    def suspend(self, name: str, namespace: str = 'default') -> Tuple[object, int, dict]:
        """Suspends a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to suspend.
        namespace: str = 'default'
            The K8S namespace of the Argo server to suspend the cron workflow on.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.suspend_cron_workflow(
            namespace,
            name,
            body=IoArgoprojWorkflowV1alpha1WorkflowSuspendRequest(name=name, namespace=namespace),
            _check_return_type=False,
        )

    def resume(self, name: str, namespace: str = 'default') -> Tuple[object, int, dict]:
        """Resumes execution of a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to resume.
        namespace: str = 'default'
            The K8S namespace of the Argo server to resume the cron workflow on.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.resume_cron_workflow(
            namespace,
            name,
            body=IoArgoprojWorkflowV1alpha1WorkflowResumeRequest(name=name, namespace=namespace),
            _check_return_type=False,
        )

    def get_cron_workflow_link(self, name: str, namespace: str = 'default') -> str:
        """Assembles a cron workflow link for the given cron workflow name. Note that the returned path works only for Argo.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to assemble a link for.
        namespace: str = 'default'
            The K8S namespace of the Argo server to get the cron workflow link from.

        Returns
        -------
        str
            The cron workflow link.
        """
        return f'{self._host}/cron-workflows/{namespace}/{name}'

    def get_workflow(self, name: str, namespace: str = 'default') -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Fetches a workflow by the specified name and namespace combination.

        Parameters
        ----------
        name: str
            Name of the workflow.
        namespace: str = 'default'
            The namespace the workflow is running in.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Workflow
        """
        return self.service.get_cron_workflow(namespace, name, _check_return_type=False)
