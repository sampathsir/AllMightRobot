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
from abc import ABCMeta
from copy import deepcopy

from ._internal import _ArgField

if typing.TYPE_CHECKING:
    from ._internal import _Parser


class ArgumentParserMeta(ABCMeta):

    def __new__(
            mcs, name: str, bases: typing.Tuple[typing.Type[ArgumentParser]], namespace: dict, **kwargs: typing.Any
    ) -> typing.Any:
        fields = {}
        parsers = {}

        # check in base class; if there is predefined
        # argument parsing methods or field declared in there
        # which would reduce code duplication
        for base in reversed(bases):
            if hasattr(base, "__ArgumentParser__") or base.__name__ != "ArgumentParser":
                fields.update(deepcopy(base.__fields__))
                parsers.update(deepcopy(base.__parsers__))

        for field in namespace:
            field_info = namespace.get(field)
            if not isinstance(field_info, _ArgField):
                mcs._extract_parsers_(parsers, field_info)
                continue

            # we allow fields to overide the fields declared in base
            # fields may not be in same index as base so uhmm!
            fields[field] = field_info

        new_namespace = {
            "__fields__": fields,
            "__parsers__": parsers,
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


class ArgumentParser(metaclass=ArgumentParserMeta):

    if typing.TYPE_CHECKING:
        __fields__: typing.Dict[typing.Any, _ArgField]
        __parsers__: typing.Dict[str, _Parser]

    __splitter__ = " "

    def __repr__(self) -> str:
        # make debugging better; inspired from pydantic
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items())
        cls = self.__class__.__name__
        return f"{cls}({attrs})"
