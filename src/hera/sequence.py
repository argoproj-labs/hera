from typing import Optional, Union

from pydantic import validator

from hera.models import IntOrString
from hera.models import Sequence as _ModelSequence


class Sequence(_ModelSequence):
    count: Optional[Union[int, str, IntOrString]] = None  # type: ignore
    end: Optional[Union[int, str, IntOrString]] = None  # type: ignore
    format: Optional[str] = None  # type: ignore
    start: Optional[Union[int, str, IntOrString]] = None  # type: ignore

    @validator("count", pre=True)
    def count_to_str(cls, v):
        if v is None:
            return v

        assert isinstance(v, int) or isinstance(v, str)
        return IntOrString(__root__=str(v))

    @validator("start", pre=True)
    def start_to_str(cls, v):
        if v is None:
            return v

        assert isinstance(v, int) or isinstance(v, str)
        return IntOrString(__root__=str(v))


__all__ = ["Sequence"]
