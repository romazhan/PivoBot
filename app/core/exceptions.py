# -*- coding: utf-8 -*-
from __future__ import annotations


class TelegramTokenError(ValueError):
    def __init__(
        self: TelegramTokenError,
        message: str,
        prepare_env_file: bool,
        *_: any
    ) -> None:
        ValueError.__init__(self, message, *_)
        prepare_env_file and self._prepare_env_file()

    def _prepare_env_file(self) -> None:
        with open('.env.example', 'r') as env_example_file:
            with open('.env', 'w') as env_file:
                env_file.write(env_example_file.read())
