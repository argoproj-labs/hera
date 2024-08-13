"""The exceptions module provides exception types required for the Hera workflows package."""


class WorkflowsException(Exception):
    """Base Hera workflows exception."""

    ...


class InvalidType(WorkflowsException):
    """Exception raised when an invalid type is submitted to a Hera object's field or functionality."""

    ...


class InvalidTemplateCall(WorkflowsException):
    """Exception raised when an invalid template call is performed."""

    ...


class InvalidDispatchType(WorkflowsException):
    """Exception raised when Hera attempts to dispatch a hook and it fails to do so."""

    ...


class TemplateNameConflict(WorkflowsException):
    """Currently unused."""

    ...


class NodeNameConflict(WorkflowsException):
    """Exception raised when multiple Task/Step are found with the same name."""

    ...


__all__ = ["InvalidType", "InvalidTemplateCall", "InvalidDispatchType", "TemplateNameConflict", "NodeNameConflict"]
