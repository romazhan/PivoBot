# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from typing import Tuple, Union
from aiogram import types

from .kernel import PivoDispatcher

from . import brain

import asyncio

import random


class _SuperChat(object, metaclass=ABCMeta):
    TYPES: Tuple[str]

    def _probably(self, percentage: int) -> bool:
        if random.choices([0, 1], weights=[100 - percentage, percentage], k=1)[0]:
            return True
        return False

    async def _simulate_printing(self, message: types.Message) -> None:
        await message.bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        await asyncio.sleep(random.uniform(1, 2.2))

    @classmethod
    @abstractmethod
    async def handle_message(self, message: types.Message) -> None:
        '''Handle this message'''


class _PrivateChat(_SuperChat):
    TYPES = ('private')
    COMMANDS = ('start', 'help')

    @classmethod
    async def handle_command(self, message: types.Message) -> None:
        command = message.text[1:]

        if command == 'start':
            await message.bot.send_message(message.from_user.id, 'Started')
        elif command == 'help':
            await message.reply('Helped')

    @classmethod
    async def handle_message(self, _: types.Message) -> None:
        pass


class _GroupChat(_PrivateChat):
    _RESPONSE_PROBABILITY = 5 # %

    TYPES = ('group', 'supergroup')

    async def _teach(self, message: types.Message) -> None:
        if message.reply_to_message:
            await brain.train(message.chat.id, message.reply_to_message.text, message.text)
    
    async def _respond(self, message: types.Message) -> Union[str, None]:
        return (await brain.answer(message.chat.id, message.text))

    @classmethod
    async def handle_message(self, message: types.Message) -> None:
        await self._teach(self, message)

        if self._probably(self, _GroupChat._RESPONSE_PROBABILITY):
            answer = await self._respond(self, message)
            if answer:
                await self._simulate_printing(self, message)
                await message.reply(answer)


# front-controller:
def init_handlers(dispatcher: PivoDispatcher) -> None:
    # private chat commands:
    @dispatcher.message_handler(
        lambda message: message.chat.type in _PrivateChat.TYPES,
        commands=_PrivateChat.COMMANDS
    )
    async def _(message: types.Message) -> None:
        await _PrivateChat.handle_command(message)


    # private chat messages:
    @dispatcher.message_handler(
        lambda message: message.chat.type in _PrivateChat.TYPES
    )
    async def _(message: types.Message) -> None:
        await _PrivateChat.handle_message(message)


    # group|supergroup messages:
    @dispatcher.message_handler(
        lambda message: message.chat.type in _GroupChat.TYPES
    )
    async def _(message: types.Message) -> None:
        await _GroupChat.handle_message(message)
