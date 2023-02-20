from dataclasses import dataclass
from typing import Optional, Union

from argo_workflows.models import IoArgoprojWorkflowV1alpha1Sequence


@dataclass
class Sequence:
    """Sequence is a representation that can be used to expand a workflow step into numeric ranges.

    Attributes
    ----------
    format: Optional[str]
        Format is a `printf` format string to format the value in the sequence.
    count: Optional[Union[int, str]]
        Number of elements in the sequence. Cannot be used with `end`.
    start: Optional[Union[int, str]]
        Number at which to start the sequence.
    end: Optional[Union[int, str]]
        Number at which to end the sequence. Cannot be used with `count`.

    Raises
    ------
    ValueError
        When both `count` and `end` are specified.
    """

    format: Optional[str] = None
    count: Optional[Union[int, str]] = None
    start: Optional[Union[int, str]] = None
    end: Optional[Union[int, str]] = None

    def __post_init__(self) -> None:
        if self.count is not None and self.end is not None:
            raise ValueError("Cannot use both `count` and `end`")
        if self.count is not None and isinstance(self.count, int):
            self.count = str(self.count)
        if self.start is not None and isinstance(self.start, int):
            self.start = str(self.start)
        if self.end is not None and isinstance(self.end, int):
            self.end = str(self.end)

    def build(self) -> IoArgoprojWorkflowV1alpha1Sequence:
        """Builds the Argo representation of the sequence.

        Returns
        -------
        IoArgoprojWorkflowV1alpha1Sequence
            The sequence to use for numeric range generation.
        """
        sequence = IoArgoprojWorkflowV1alpha1Sequence()
        if self.format is not None:
            setattr(sequence, "format", self.format)
        if self.count is not None:
            setattr(sequence, "count", self.count)
        if self.start is not None and self.end is not None:
            setattr(sequence, "start", self.start)
            setattr(sequence, "end", self.end)
        return sequence
