# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from typing import Tuple, Union

from aiogram import types, utils

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

    async def _simulate_printing(self, message: types.Message, text: str = 'average text') -> None:
        delay = len(text) * 0.19

        await message.bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        await asyncio.sleep(random.uniform(
            delay, delay + random.uniform(0.1, 0.8)
        ))

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
    _TRIGGERS = (
        'пиво', 'пива', 'пивас', 'пивасик', 'бот', 'ботик'
    )
    _RESPONSE_PROBABILITY = 30 # %

    TYPES = ('group', 'supergroup')
    COMMANDS = ('pivo')

    def _triggered(self, message: types.Message) -> bool:
        try:
            if message.reply_to_message.from_id == message.bot.id:
                return True
        except AttributeError:
            pass

        triggers = set(_GroupChat._TRIGGERS)
        message_list = message.text.lower().split(' ')

        if triggers.intersection(message_list):
            trigerred_message = ' '.join(list(set(message_list) - triggers)).strip()

            if trigerred_message:
                message.text = trigerred_message
                return True

        return False

    async def _teach(self, message: types.Message) -> None:
        if message.reply_to_message:
            await brain.train(message.chat.id, message.reply_to_message.text, message.text)
    
    async def _respond(self, message: types.Message) -> Union[str, None]:
        return (await brain.answer(message.chat.id, message.text))

    @classmethod
    async def handle_command(self, message: types.Message) -> None:
        command = message.text

        if command.startswith('/pivo'):
            await message.reply(f'''{message.from_user.first_name}, {random.choice((
                'наливаю кружку свежего 🍺',
                'наливаю 2 кружки мощного 🍺🍺',
                'тебе аж 3 кружки 🍺🍺🍺 🥰',
                'ты сегодня чемпион, выпей пива - ты галон 😘🥶😜'
            ))}''')

    @classmethod
    async def handle_message(self, message: types.Message) -> None:
        await self._teach(self, message)

        if self._probably(self, _GroupChat._RESPONSE_PROBABILITY) or self._triggered(self, message):
            answer = await self._respond(self, message)
            if answer:
                await self._simulate_printing(self, message, answer)

                try:
                    await message.reply(answer)
                except utils.exceptions.MessageToReplyNotFound:
                    await message.bot.send_message(message.chat.id, 'Удалил, да? 🫡')


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


    # group|supergroup commands:
    @dispatcher.message_handler(
        lambda message: message.chat.type in _GroupChat.TYPES,
        commands=_GroupChat.COMMANDS
    )
    async def _(message: types.Message) -> None:
        await _GroupChat.handle_command(message)


    # group|supergroup messages:
    @dispatcher.message_handler(
        lambda message: message.chat.type in _GroupChat.TYPES
    )
    async def _(message: types.Message) -> None:
        await _GroupChat.handle_message(message)
