import os
import logging
from dataclasses import dataclass


CLIENT_KEY_ENV_VAR = "YSC_CLIENT_KEY"
SERVER_KEY_ENV_VAR = "YSC_SERVER_KEY"


@dataclass
class Config:
    enabled: bool
    client_key: str = ""
    server_key: str = ""

    @classmethod
    def from_env(cls, logger: logging.Logger):
        client_key = os.getenv(CLIENT_KEY_ENV_VAR)
        if client_key is None:
            logger.warning(
                f"Captcha is disabled because variable {CLIENT_KEY_ENV_VAR} is not present in environment"
            )
            return cls(enabled=False)

        server_key = os.getenv(SERVER_KEY_ENV_VAR)
        if server_key is None:
            logger.warning(
                f"Captcha is disabled because variable {SERVER_KEY_ENV_VAR} is not present in environment"
            )
            return cls(enabled=False)

        return cls(
            enabled=True,
            client_key=client_key,
            server_key=server_key,
        )
