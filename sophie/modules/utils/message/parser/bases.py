# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Sophie.

from __future__ import annotations

import typing
import inspect

from abc import ABCMeta, abstractmethod
from copy import deepcopy

from ._internal import _ArgField

if typing.TYPE_CHECKING:
    from aiogram.api.types import Message
    from ._internal import _Parser


class ArgumentParserMeta(ABCMeta):

    def __new__(
            mcs, name: str, bases: typing.Tuple[typing.Type[ArgumentParser]], namespace: dict, **kwargs: typing.Any
    ) -> typing.Any:
        fields = {}
        parsers = {}
        root_parser = None

        # check in base class; if there is predefined
        # argument parsing methods or field declared in there
        # which would reduce code duplication
        for base in reversed(bases):
            if hasattr(base, "__ArgumentParser__") or base.__name__ != "ArgumentParser":
                fields.update(deepcopy(base.__fields__))
                parsers.update(deepcopy(base.__parsers__))
                root_parser = base.__root_parser__

        for field in namespace:
            field_info = namespace.get(field)
            if not isinstance(field_info, _ArgField):
                mcs._extract_parsers_(parsers, field_info)

                if field_info is not None and inspect.isclass(field_info):
                    if issubclass(field_info, BaseRootParser):
                        root_parser = field_info
                continue

            # we allow fields to overide the fields declared in base
            # fields may not be in same index as base so uhmm!
            fields[field] = field_info

        new_namespace = {
            "__fields__": fields,
            "__parsers__": parsers,
            "__root_parser__": root_parser,
            "__ArgumentParser__": True,
            **{name: value for name, value in namespace.items() if name not in (fields or parsers)},
        }
        new_namespace["__namespace__"] = new_namespace  # save a snapshot of new namespace
        cls = super().__new__(mcs, name, bases, new_namespace)
        return cls

    @classmethod
    def _extract_parsers_(mcs, parsers: dict, field_data: typing.Any) -> typing.Any:
        if isinstance(field_data, classmethod):  # parsers would be classmethods
            attr = getattr(field_data, "__parser_method__", None)  # ((field1, field2, ...), <parser>)
            if attr:
                for field in attr[0]:
                    parsers[field] = attr[1]


class BaseRootParser(metaclass=ABCMeta):
    """
    Root parsers are used to process the text in a custom way.

    All you need to do is return the ``list of anything`` (in function `get_text`)
    that is processed, should fit the index defined by fields
    """

    @abstractmethod
    async def get_text(
            self, message: Message, text: typing.Optional[str], fields: dict
    ) -> list:
        """
        :param message: Message object
        :param text: return the whole text deducting the ``/command``
        :param fields: fields defined in the class
        """
        raise NotImplementedError


class ArgumentParser(metaclass=ArgumentParserMeta):

    if typing.TYPE_CHECKING:
        __fields__: typing.Dict[typing.Any, _ArgField]
        __parsers__: typing.Dict[str, _Parser]
        __root_parser__: typing.Optional[typing.Type[BaseRootParser]]

    __splitter__ = " "

    def __repr__(self) -> str:
        # make debugging better; inspired from pydantic
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items())
        cls = self.__class__.__name__
        return f"{cls}({attrs})"
