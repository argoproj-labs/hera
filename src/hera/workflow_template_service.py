"""Custom WorkflowTemplate Service class"""
from typing import Optional, Tuple

from argo_workflows.apis import WorkflowTemplateServiceApi
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1WorkflowTemplate,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateCreateRequest,
)

from hera.client import Client
from hera.config import Config


class WorkflowTemplateService:
    """Argo workflowTemplate service for performing actions against workflowTemplate - creations, deletions

    Parameters
    ----------
    host: Optional[str] = None
        The host of the Argo server to submit workflowTemplate to. An attempt to assemble a host from Argo K8S cluster
        environment variables is pursued if this is not specified.
    verify_ssl: bool = True
        Whether to perform SSL/TLS verification. Set this to false to skip verifying SSL certificate when submitting
        workflowTemplate from an HTTPS server.
    token: Optional[str] = None
        The token to use for authentication purposes. Note that this assumes the Argo deployment is fronted with a
        deployment/service that can intercept a request and check the Bearer token.
    namespace: str = 'default'
        The K8S namespace the workflowTemplate service creates workflowTemplate in.
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
        self.service = WorkflowTemplateServiceApi(api_client=api_client)

    def create(
        self, workflow_template: IoArgoprojWorkflowV1alpha1WorkflowTemplate, namespace: str = 'default'
    ) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Creates given workflowTemplate in the argo server.

        Parameters
        ----------
        workflow_template: V1alpha1WorkflowTemplate
            The workflowTemplate to create.
        namespace: str = 'default'
            The K8S namespace of the Argo server to create the workflowTemplate in.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1WorkflowTemplate
            The created workflowTemplate.

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.create_workflow_template(
            namespace,
            IoArgoprojWorkflowV1alpha1WorkflowTemplateCreateRequest(template=workflow_template, _check_type=False),
            _check_return_type=False,
        )

    def delete(self, name: str, namespace: str = 'default') -> Tuple[object, int, dict]:
        """Deletes a workflow template from the given namespace based on the specified name.

        Parameters
        ----------
        name: str
            The name of the workflow template to delete.
        namespace: str = 'default'
            The K8S namespace of the Argo server to delete the workflow template from.

        Returns
        -------
            Tuple(object, status_code(int), headers(HTTPHeaderDict))

        Raises
        ------
        argo.workflows.client.ApiException: Raised upon any HTTP-related errors
        """
        return self.service.delete_workflow_template(namespace, name)
