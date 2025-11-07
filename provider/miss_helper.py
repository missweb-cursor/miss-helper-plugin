from typing import Any
from dify_plugin import ToolProvider


class MissHelperProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the credentials for the Miss Helper provider.
        This plugin doesn't require credentials, so validation always passes.
        """
        # No credentials required for this provider
        pass
