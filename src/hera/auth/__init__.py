import shutil
import subprocess


class TokenGenerator:
    """A token generator can be used to generate tokens for authentication with Argo Workflows/Events APIs.

    A token generator can be set for invocation on the Hera global config via
    `hera.shared.global_config.token`.
    """

    def __call__(self) -> str:
        """Generates an authentication token for use with Argo Workflows/Events APIs"""
        raise NotImplementedError("Implement me")


class ArgoCLITokenGenerator(TokenGenerator):
    """A token generator that uses the Argo CLI to generate a token.

    Note that this involves invoking the Argo CLI, which means that the Argo CLI must be installed on the machine.
    An exception is raised if this is not the case.

    Raises
    ------
    RuntimeError
        If the Argo CLI is not installed.
    """

    def __call__(self) -> str:
        if shutil.which("argo") is None:
            raise RuntimeError(
                "The Argo CLI is not installed. "
                "See `https://argoproj.github.io/argo-workflows/walk-through/argo-cli/` for more information"
            )

        token = subprocess.check_output("argo auth token".split()).strip().decode()
        if token.startswith("Bearer "):
            token = token[7:]
        return token
