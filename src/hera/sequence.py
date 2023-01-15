from typing import Optional, Union

from pydantic import validator

from hera.models import IntOrString
from hera.models import Sequence as _ModelSequence


class Sequence(_ModelSequence):
    count: Optional[Union[int, str, IntOrString]] = None
    end: Optional[Union[int, str, IntOrString]] = None
    format: Optional[str] = None
    start: Optional[Union[int, str, IntOrString]] = None

    @validator("count", pre=True)
    def count_to_str(cls, v):
        if v is None:
            return v

        assert isinstance(v, int) or isinstance(v, str)
        if isinstance(v, str):
            return IntOrString(__root__=v)
        return IntOrString(__root__=str(v))

    @validator("start", pre=True)
    def start_to_str(cls, v):
        if v is None:
            return v

        assert isinstance(v, int) or isinstance(v, str)
        if isinstance(v, str):
            return IntOrString(__root__=v)
        return IntOrString(__root__=str(v))

    @validator("start", pre=True)
    def end_to_str(cls, v):
        if v is None:
            return v

        assert isinstance(v, int) or isinstance(v, str)
        if isinstance(v, str):
            return IntOrString(__root__=v)
        return IntOrString(__root__=str(v))


__all__ = ["Sequence"]
