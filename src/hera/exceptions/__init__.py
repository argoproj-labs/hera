"""Module that holds Hera specific exceptions.

These are thin wrappers around the core Python `Exception`.
"""
import json
from http import HTTPStatus
from typing import Dict, Type

from requests import Response


class HeraException(Exception):
    """Base class for exceptions in this module."""

    status_code: int


class Unauthorized(HeraException):
    status_code = HTTPStatus.UNAUTHORIZED.value


class BadRequest(HeraException):
    status_code = HTTPStatus.BAD_REQUEST.value


class Forbidden(HeraException):
    status_code = HTTPStatus.FORBIDDEN.value


class NotFound(HeraException):
    status_code = HTTPStatus.NOT_FOUND.value


class NotImplemented(HeraException):
    status_code = HTTPStatus.NOT_IMPLEMENTED.value


class AlreadyExists(HeraException):
    status_code = HTTPStatus.CONFLICT.value


class InternalServerError(HeraException):
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
    """Returns a `HeraException` mapped from the given status code initialized with the given message"""
    return status_code_to_exception_map.get(status_code, HeraException)(msg)


def exception_from_server_response(resp: Response) -> HeraException:
    """Returns a `HeraException` mapped from the given `Response`"""
    assert not resp.ok, "This function should only be called with non-2xx responses"
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
