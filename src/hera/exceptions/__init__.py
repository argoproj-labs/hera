"""Module that holds Hera specific exceptions.

These are thin wrappers around the core Python `Exception`. Some exceptions are used for indicating any errors
encountered when communication with the Argo server.
"""

import json
from http import HTTPStatus
from typing import TYPE_CHECKING, Dict, Type, Union

from requests import Response

if TYPE_CHECKING:
    import httpx


class HeraException(Exception):
    """Base class for exceptions in this module."""

    status_code: int


class Unauthorized(HeraException):
    """Exception that indicates the server did not authorize the request."""

    status_code = HTTPStatus.UNAUTHORIZED.value


class BadRequest(HeraException):
    """Exception that indicates the server received a bad request."""

    status_code = HTTPStatus.BAD_REQUEST.value


class Forbidden(HeraException):
    """Exception that indicates the server received the request but it is forbidden."""

    status_code = HTTPStatus.FORBIDDEN.value


class NotFound(HeraException):
    """Exception that indicates a requested resource was not found."""

    status_code = HTTPStatus.NOT_FOUND.value


class NotImplemented(HeraException):
    """Exception that indicates a particular method is not implemented on the server side."""

    status_code = HTTPStatus.NOT_IMPLEMENTED.value


class AlreadyExists(HeraException):
    """Exception that indicates a conflict was encountered when creating a specific resource."""

    status_code = HTTPStatus.CONFLICT.value


class InternalServerError(HeraException):
    """Exception that indicates something went wrong on the server side."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value


status_code_to_exception_map: Dict[int, Type[HeraException]] = {
    Unauthorized.status_code: Unauthorized,
    BadRequest.status_code: BadRequest,
    Forbidden.status_code: Forbidden,
    NotFound.status_code: NotFound,
    NotImplemented.status_code: NotImplemented,
    AlreadyExists.status_code: AlreadyExists,
    InternalServerError.status_code: InternalServerError,
}


def exception_from_status_code(status_code: int, msg: str) -> HeraException:
    """Return a `HeraException` mapped from the given status code initialized with the given message."""
    return status_code_to_exception_map.get(status_code, HeraException)(msg)


def exception_from_server_response(resp: Union[Response, "httpx.Response"]) -> HeraException:
    """Return a `HeraException` mapped from the given `Response`."""
    is_success = resp.ok if isinstance(resp, Response) else resp.is_success
    assert not is_success, "This function should only be called with non-2xx responses"
    try:
        return exception_from_status_code(
            resp.status_code,
            f"Server returned status code {resp.status_code} with message: `{resp.json()['message']}`",
        )
    except json.JSONDecodeError:
        return exception_from_status_code(
            resp.status_code,
            f"Server returned status code {resp.status_code} with message: `{resp.text}`",
        )
