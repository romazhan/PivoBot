# -*- coding: utf-8 -*-
from typing import List, Union

from fuzzywuzzy import utils, process, fuzz

from os.path import exists

import random

import re


class _Brain(object):
    _TEXT_LENGTH_RANGE = (2, 125)

    _Q, _A = 'q:', 'a:'
    _GAP = '\n'

    _QA_TEMPLATE = 'q:{0}\na:{1}\n'
    _QS_THRESHOLD = 80
    _QS_MAX_COUNT = 8

    _BRAIN_PATH = './brain'
    _BRAIN_ENCODING = 'utf-8'

    _MEMORY_EXTENSION = '.memory'

    def _get_memory_path(self, chat_id: int) -> str:
        path = f'{_Brain._BRAIN_PATH}/{chat_id}{_Brain._MEMORY_EXTENSION}'
        if not exists(path):
            with open(path, 'w'): pass
        return path

    def _clear_qa(self, qa: str) -> str:
        return qa.replace(_Brain._Q, '').replace(_Brain._A, '').replace(_Brain._GAP, '')

    def _clear_text(self, text: str) -> Union[str, None]:
        strip_extra_spaces = lambda t: re.sub(r'\s+', ' ', str(t)).strip()
        normalize_punctuation = lambda t: re.sub(r'\s+(?=(?:[,.?!:;…]))', '', t)
        clear_characters = lambda t: re.sub(r'[^А-яё0-9@,.!?.,:;()"*\-+= ]+', '', t).lower().strip()

        stripped_text = strip_extra_spaces(text)
        normalized_text = normalize_punctuation(stripped_text)

        if len(normalized_text) > _Brain._TEXT_LENGTH_RANGE[1]:
            return None

        cleared_text = strip_extra_spaces(normalize_punctuation(
            clear_characters(normalized_text)
        ))

        if len(cleared_text) < _Brain._TEXT_LENGTH_RANGE[0]:
            return None

        return cleared_text

    def _get_qs(self, chat_id: int) -> List[str]:
        '''Get questions from memory'''
        qs = []

        with open(self._get_memory_path(self, chat_id), 'r', encoding=_Brain._BRAIN_ENCODING) as f:
            for line in f:
                if line.startswith(_Brain._Q):
                    qs.append(self._clear_qa(self, line))
        
        return qs
    
    def _get_a_from_q(self, chat_id: int, q: str, all_a = False) -> Union[str, Union[List, List[str]], None]:
        a = None

        with open(self._get_memory_path(self, chat_id), 'r', encoding=_Brain._BRAIN_ENCODING) as f:
            cached_answers = []
            a_is_found = False

            for line in f:
                if a_is_found:
                    a = cached_answers.append(self._clear_qa(self, line))
                    a_is_found = False
                    continue
                if line.startswith(_Brain._Q) and self._clear_qa(self, line) == q:
                    a_is_found = True
            
            if all_a:
                a = cached_answers
            elif cached_answers:
                a = random.choice(cached_answers)

        return a

    @classmethod
    async def learn(self, chat_id: int, q: str, a: str) -> bool:
        q, a = self._clear_text(self, q), self._clear_text(self, a)

        if q and a and len(self._get_a_from_q(self, chat_id, q, True)) <= _Brain._QS_MAX_COUNT:
            with open(self._get_memory_path(self, chat_id), 'a', encoding=_Brain._BRAIN_ENCODING) as f:
                f.write(_Brain._QA_TEMPLATE.format(q, a))
        
    @classmethod
    async def get_answer(self, chat_id: int, q: str) -> Union[str, None]:
        q = self._clear_text(self, q)
        if not q:
            return None

        answer = None
        extracted_qs = ()
        if utils.full_process(q):
            extracted_qs = process.extract(
                q, self._get_qs(self, chat_id), limit=_Brain._QS_MAX_COUNT, scorer=fuzz.token_set_ratio
            )
        
        if extracted_qs:
            processed_qs = []

            for e_q in extracted_qs:
                if e_q[1] >= _Brain._QS_THRESHOLD:
                    processed_qs.append(e_q[0])
            
            if processed_qs:
                final_q = random.choice(processed_qs)
                answer = self._get_a_from_q(self, chat_id, final_q)
        
        return (answer.capitalize() if answer else None)


async def train(chat_id: int, q: str, a: str) -> None:
    await _Brain.learn(chat_id, q, a)


async def answer(chat_id: int, q: str) -> Union[str, None]:
    return (await _Brain.get_answer(chat_id, q))
