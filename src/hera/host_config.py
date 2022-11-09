from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Optional, Union

_api_version: str = "argoproj.io/v1alpha1"


def set_global_api_version(v: str) -> None:
    """Sets the global API version that is used to control the `api_version` field on Argo payload submissions.

    Workflows, workflow templates, etc. use an API specification that is based on the requirements of Kubernetes:
    https://kubernetes.io/docs/reference/using-api/#api-versioning
    """
    warnings.warn(
        "`host_config.set_global_api_version` is deprecated in favor of "
        "`global_config.GlobalConfig.api_version` and will be removed in a future version"
    )
    global _api_version
    _api_version = v


def get_global_api_version() -> str:
    """Returns the set global API version. See `set_global_api_version` for more details"""
    warnings.warn(
        "`host_config.get_global_api_version` is deprecated in favor of "
        "`global_config.GlobalConfig.api_version` and will be removed in a future version"
    )
    global _api_version
    return _api_version


_service_account_name: Optional[str] = None


def set_global_service_account_name(sa: Optional[str]) -> None:
    """Sets the service account to use for workflow submissions on a global level"""
    warnings.warn(
        "`host_config.set_global_service_account_name` is deprecated in favor of "
        "`global_config.GlobalConfig.service_account_name` and will be removed in a future version"
    )
    global _service_account_name
    _service_account_name = sa


def get_global_service_account_name() -> Optional[str]:
    """Returns the set global service account"""
    warnings.warn(
        "`host_config.get_global_service_account_name` is deprecated in favor of "
        "`global_config.GlobalConfig.service_account_name` and will be removed in a future version"
    )
    global _service_account_name
    return _service_account_name


_verify_ssl: bool = True


def set_global_verify_ssl(v: bool) -> None:
    """Sets the flag for whether to verify SSL on workflow submission globally.

    Set this as False to skip verifying SSL certificate when submitting workflows from an HTTPS server.
    """
    warnings.warn(
        "`host_config.set_global_verify_ssl` is deprecated in favor of "
        "`global_config.GlobalConfig.verify_ssl` and will be removed in a future version"
    )
    global _verify_ssl
    _verify_ssl = v


def get_global_verify_ssl() -> bool:
    """Returns the set global verify SSL option"""
    warnings.warn(
        "`host_config.get_global_verify_ssl` is deprecated in favor of "
        "`global_config.GlobalConfig.verify_ssl` and will be removed in a future version"
    )
    global _verify_ssl
    return _verify_ssl


_host: Optional[str] = None


def set_global_host(h: Optional[str]) -> None:
    """Sets the Argo Workflows host at a global level so services can use it"""
    warnings.warn(
        "`host_config.set_global_host` is deprecated in favor of "
        "`global_config.GlobalConfig.host` and will be removed in a future version"
    )
    global _host
    _host = h


def get_global_host() -> Optional[str]:
    """Returns the Argo Workflows global host"""
    warnings.warn(
        "`host_config.get_global_host` is deprecated in favor of "
        "`global_config.GlobalConfig.host` and will be removed in a future version"
    )
    return _host


_token: Union[Optional[str], Callable[[], Optional[str]]] = None


def set_global_token(t: Union[Optional[str], Callable[[], Optional[str]]]) -> None:
    """Sets the Argo Workflows token at a global level so services can use it"""
    warnings.warn(
        "`host_config.set_global_token` is deprecated in favor of "
        "`global_config.GlobalConfig.token` and will be removed in a future version"
    )
    global _token
    _token = t


def get_global_token() -> Optional[str]:
    """Returns an Argo Workflows global token"""
    warnings.warn(
        "`host_config.get_global_token` is deprecated in favor of "
        "`global_config.GlobalConfig.token` and will be removed in a future version"
    )
    if _token is None or isinstance(_token, str):
        return _token
    return _token()


_namespace: str = "default"


def set_global_namespace(n: str) -> None:
    """Sets the Argo Workflows namespace at the global level so services can use it"""
    warnings.warn(
        "`host_config.set_global_namespace` is deprecated in favor of "
        "`global_config.GlobalConfig.namespace` and will be removed in a future version"
    )
    global _namespace
    _namespace = n


def get_global_namespace() -> str:
    """Returns the Argo Workflows global namespace"""
    warnings.warn(
        "`host_config.get_global_namespace` is deprecated in favor of "
        "`global_config.GlobalConfig.namespace` and will be removed in a future version"
    )
    return _namespace


_image: str = "python:3.7"


def set_global_task_image(image: str) -> None:
    """Sets the Argo Task image at the global level which Tasks will use by default"""
    warnings.warn(
        "`host_config.set_global_task_image` is deprecated in favor of "
        "`global_config.GlobalConfig.image` and will be removed in a future version"
    )
    global _image
    _image = image


def get_global_task_image() -> str:
    """Returns the Argo Task global image"""
    warnings.warn(
        "`host_config.get_global_task_image` is deprecated in favor of "
        "`global_config.GlobalConfig.image` and will be removed in a future version"
    )
    return _image
