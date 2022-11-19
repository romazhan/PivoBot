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

    async def _simulate_printing(self, msg: types.Message, text: str = 'average text') -> None:
        delay = len(text) * 0.19

        await msg.bot.send_chat_action(msg.chat.id, types.ChatActions.TYPING)
        await asyncio.sleep(random.uniform(
            delay, delay + random.uniform(0.1, 0.8)
        ))

    @classmethod
    @abstractmethod
    async def handle_msg(self, msg: types.Message) -> None:
        '''Handle this message'''


class _PrivateChat(_SuperChat):
    TYPES = ('private')
    COMMANDS = ('start', 'help')

    @classmethod
    async def handle_command(self, msg: types.Message) -> None:
        command = msg.text[1:]

        if command == 'start':
            await msg.bot.send_message(msg.from_user.id, 'Started')
        elif command == 'help':
            await msg.reply('Helped')

    @classmethod
    async def handle_msg(self, _: types.Message) -> None:
        pass


class _GroupChat(_PrivateChat):
    _TRIGGERS = (
        'пиво', 'пива', 'пивас', 'пивасик', 'бот', 'ботик'
    )
    _RESPONSE_PROBABILITY = 20 # %

    TYPES = ('group', 'supergroup')
    COMMANDS = ('pivo')

    def _triggered(self, msg: types.Message) -> bool:
        try:
            if msg.reply_to_message.from_id == msg.bot.id:
                return True
        except AttributeError:
            pass

        triggers = set(_GroupChat._TRIGGERS)
        msg_list = msg.text.lower().split(' ')

        if triggers.intersection(msg_list):
            trigerred_msg = ' '.join(list(set(msg_list) - triggers)).strip()

            if trigerred_msg:
                msg.text = trigerred_msg
                return True

        return False

    async def _teach(self, msg: types.Message) -> None:
        if msg.reply_to_message:
            await brain.train(msg.chat.id, msg.reply_to_message.text, msg.text)
    
    async def _respond(self, msg: types.Message) -> Union[str, None]:
        return (await brain.answer(msg.chat.id, msg.text))

    @classmethod
    async def handle_command(self, msg: types.Message) -> None:
        command = msg.text

        if command.startswith('/pivo'):
            await msg.reply(f'''{msg.from_user.first_name}, {random.choice((
                'наливаю кружку свежего 🍺',
                'наливаю 2 кружки мощного 🍺🍺',
                'тебе аж 3 кружки 🍺🍺🍺 🥰',
                'ты сегодня чемпион, выпей пива - ты галон 😘🥶😜'
            ))}''')

    @classmethod
    async def handle_msg(self, msg: types.Message) -> None:
        await self._teach(self, msg)

        if self._probably(self, _GroupChat._RESPONSE_PROBABILITY) or self._triggered(self, msg):
            answer = await self._respond(self, msg)
            if answer:
                await self._simulate_printing(self, msg, answer)

                try:
                    await msg.reply(answer)
                except utils.exceptions.MessageToReplyNotFound:
                    await msg.bot.send_message(msg.chat.id, 'Удалил, да? 🫡')


# front-controller:
def init_handlers(dispatcher: PivoDispatcher) -> None:
    # private chat commands:
    @dispatcher.message_handler(
        lambda msg: msg.chat.type in _PrivateChat.TYPES,
        commands=_PrivateChat.COMMANDS
    )
    async def _(msg: types.Message) -> None:
        await _PrivateChat.handle_command(msg)


    # private chat messages:
    @dispatcher.message_handler(
        lambda msg: msg.chat.type in _PrivateChat.TYPES
    )
    async def _(msg: types.Message) -> None:
        await _PrivateChat.handle_msg(msg)


    # group|supergroup commands:
    @dispatcher.message_handler(
        lambda msg: msg.chat.type in _GroupChat.TYPES,
        commands=_GroupChat.COMMANDS
    )
    async def _(msg: types.Message) -> None:
        await _GroupChat.handle_command(msg)


    # group|supergroup messages:
    @dispatcher.message_handler(
        lambda msg: msg.chat.type in _GroupChat.TYPES
    )
    async def _(msg: types.Message) -> None:
        await _GroupChat.handle_msg(msg)
