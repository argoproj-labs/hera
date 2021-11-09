"""Holds the cron workflow service that supports client cron workflow submissions"""
from typing import Tuple, Optional

from argo.workflows.client import (
    V1alpha1CronWorkflow,
    CronWorkflowServiceApi,
    V1alpha1CreateCronWorkflowRequest,
    V1alpha1CronWorkflowSuspendRequest,
    V1alpha1CronWorkflowResumeRequest,
)
from hera.v1.client import Client
from hera.v1.config import Config


class CronWorkflowService:
    """Argo cron workflow service for performing actions against cron workflows - submissions, deletions, etc.

    Parameters
    ----------
    domain: str
        The Argo deployment domain to submit cron workflows to.
    token: str
        The token to use for authentication purposes. Note that this assumes the Argo deployment is fronted with a
        deployment/service that can intercept a request and check the Bearer token.
    namespace: str = 'default'
        The K8S namespace the cron workflow service submits cron workflows to.
        This defaults to the `default` namespace.
    """

    def __init__(self, domain: str, token: str, namespace: str = 'default'):
        self._domain = domain
        self._namespace = namespace
        api_client = Client(Config(domain), token).api_client
        self.service = CronWorkflowServiceApi(api_client=api_client)

    def submit(self, cron_workflow: V1alpha1CronWorkflow, namespace: Optional[str] = None) -> V1alpha1CronWorkflow:
        """Submits the given cron workflow to the given namespace.

        Parameters
        ----------
        cron_workflow: V1alpha1CronWorkflow
            The cron workflow to submit.
        namespace: Optional[str] = None
            The K8S namespace of the Argo server to submit the cron workflow to.

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        namespace = namespace or self._namespace
        return self.service.create_cron_workflow(
            namespace, V1alpha1CreateCronWorkflowRequest(cron_workflow=cron_workflow)
        )

    def delete(self, name: str, namespace: Optional[str] = None) -> Tuple[object, int, dict]:
        """Deletes a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: str
            The name of the cron workflow to delete.
        namespace: optional str
            The K8S namespace of the Argo server to delete the cron workflow from.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        namespace = namespace or self._namespace
        return self.service.delete_cron_workflow(namespace, name)

    def suspend(self, name: str, namespace: Optional[str] = None) -> Tuple[object, int, dict]:
        """Suspends a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to suspend.
        namespace: optional str
            The K8S namespace of the Argo server to suspend the cron workflow on.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        namespace = namespace or self._namespace
        return self.service.suspend_cron_workflow(
            namespace, name, body=V1alpha1CronWorkflowSuspendRequest(name=name, namespace=namespace)
        )

    def resume(self, name: str, namespace: Optional[str] = None) -> Tuple[object, int, dict]:
        """Resumes execution of a cron workflow from the given namespace based on the specified name.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to resume.
        namespace: optional str
            The K8S namespace of the Argo server to resume the cron workflow on.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        namespace = namespace or self._namespace
        return self.service.resume_cron_workflow(
            namespace, name, body=V1alpha1CronWorkflowResumeRequest(name=name, namespace=namespace)
        )

    def get_cron_workflow_link(self, name: str, namespace: Optional[str] = None) -> str:
        """Assembles a cron workflow link for the given cron workflow name. Note that the returned path works only for Argo.

        Parameters
        ----------
        name: optional str
            The name of the cron workflow to assemble a link for.
        namespace: optional str
            The K8S namespace of the Argo server to get the cron workflow link from.

        Returns
        -------
        str
            The cron workflow link.
        """
        namespace = namespace or self._namespace
        return f'https://{self._domain}/cron-workflows/{namespace}/{name}'
