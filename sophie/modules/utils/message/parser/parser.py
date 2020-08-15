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

import inspect
import typing

from contextlib import suppress

from .errors import NoArgsGivenError, MissingField
from .fields import Undefined

if typing.TYPE_CHECKING:
    from aiogram.api.types import Message
    from .bases import ArgumentParser


async def _parse(
        cls: typing.Type[ArgumentParser],
        message: Message,
        text: typing.Optional[str],
        allow_missing: bool,
        skip_command: bool = False
) -> typing.Any:

    fields = cls.__fields__
    parsers = cls.__parsers__
    values = {}
    transporter = None  # an medium to allow fields to communicate each other

    _text_is_none = False
    if text is None and not allow_missing:
        raise NoArgsGivenError

    # check whether text's first word is a command
    # why message.text ? caption doesnt count as a command text, whatever!
    if message.text is not None:
        if message.text.startswith("/") and not skip_command:
            cmd_text = message.text.split(maxsplit=1)
            if len(cmd_text) == 1:
                # seems empty args
                if allow_missing:
                    text = None
                else:
                    raise NoArgsGivenError
            else:
                text = cmd_text[-1]

    if text is not None:
        parsed_text = text.split(cls.__splitter__)
        index = len(parsed_text) - 1
    else:
        index = 0
        parsed_text = []
        _text_is_none = True

    for field in cls.__fields__:
        field_info = fields[field]

        max_index = 0
        if isinstance(field_info.index, int):
            max_index = field_info.index
        elif isinstance(field_info.index, slice):
            max_index = field_info.index.stop if field_info.index.stop else field_info.index.start
        else:
            _text_is_none = True

        if _text_is_none or max_index > index:
            if field_info.default is not Undefined:
                values[field] = field_info.default
                continue
            elif field_info.allow_none:
                values[field] = None
                continue
            else:
                raise MissingField(field, field_info)
        else:
            if parser := parsers.get(field, None):
                args: typing.List[typing.Any] = [message]
                if parser.whole_text:
                    args.append(text)
                else:
                    args.append(parsed_text[field_info.index])

                if parser.last_fields:
                    args.append(values.get(list(values.keys())[-1]))  # get last field value n pass it

                if parser.communicate:
                    args.append(transporter)

                if inspect.iscoroutinefunction(parser.parser):
                    parsed = await parser.parser(cls, *args)
                else:
                    parsed = parser.parser(cls, *args)

                value = parsed
                if isinstance(parsed, tuple) and len(parsed) > 0:
                    value = parsed[0]  # first item should be the parsed value
                    with suppress(IndexError):
                        transporter = parsed[1:]  # rest should be communications

                if not value:
                    raise MissingField(field, field_info)

                values[field] = value
            else:
                values[field] = parsed_text[field_info.index]

    instance = cls()
    setattr(instance, "__dict__", values)  # noqa
    return instance
