"""The entrypoint for the Hera Runner when running on Argo."""

import os
from typing import Any, Tuple, Union

from hera.workflows._runner.util import _run


class RunnerException(Exception):
    """An exception class that can hold outputs to write to file on Argo before passing the exception up.

    Note: Must be enabled via hera.shared.global_config.experimental_features.
    """

    def __init__(self, outputs: Union[Tuple[Any], Any]) -> None:
        """Initialise the RunnerException with outputs to be written that match the function output annotations."""
        if os.environ.get("hera__script_runner_exception", None) is None:
            raise ValueError(
                (
                    "Unable to instantiate {} since it is an experimental feature."
                    " Please turn on experimental features by setting "
                    '`hera.shared.global_config.experimental_features["{}"] = True`.'
                    " Note that experimental features are unstable and subject to breaking changes."
                ).format(RunnerException, "script_runner_exception")
            )
        self.outputs = outputs


if __name__ == "__main__":
    _run()
