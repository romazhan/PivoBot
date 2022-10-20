# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Tuple

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import aiogram.utils as utils

from .exceptions import TelegramTokenError

from datetime import datetime
from time import sleep

import gc


class PivoBot(Bot):
    _PARSE_MODE = types.ParseMode.HTML
    _DELAY_FOR_RESTART = 5 # sec.

    def __init__(self: PivoBot, telegram_token: str) -> None:
        Bot.__init__(self, telegram_token, parse_mode=PivoBot._PARSE_MODE)
        self._id = int(telegram_token.split(':')[0])
        self._dispatcher = PivoDispatcher(self)

    def _print_start_report(self) -> None:
        print(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}]: PivoBot started ~")

    def get_instance(self) -> Tuple[PivoBot, PivoDispatcher]:
        return (self, self._dispatcher)

    def run(self) -> None:
        self._print_start_report()
        try:
            utils.executor.start_polling(self._dispatcher, skip_updates=True)

        except utils.exceptions.Unauthorized:
            raise TelegramTokenError('inactive TELEGRAM_TOKEN', False)

        except Exception as unhandled_error:
            print(f'[unhandled_error]: {unhandled_error}')
            sleep(PivoBot._DELAY_FOR_RESTART)

            gc.collect()
            self.run()


class PivoDispatcher(Dispatcher):
    pass
