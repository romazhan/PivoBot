# -*- coding: utf-8 -*-
from core.exceptions import TelegramTokenError

from core.kernel import PivoBot
from core.startum import init_handlers

from dotenv import load_dotenv
from sys import argv
import os


def self_init() -> PivoBot:
    ROOT = os.path.dirname(argv[0])
    ROOT and os.chdir(ROOT)

    load_dotenv('./.env')

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        raise TelegramTokenError('empty TELEGRAM_TOKEN in .env', True)

    bot, dispatcher = PivoBot(TOKEN).get_instance()
    init_handlers(dispatcher)

    return bot

if __name__ == '__main__':
    self_init().run()
