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

from .errors import NoArgsGivenError, MissingField, SkipParsing
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

    # vars
    values = {}
    skipped_indexes = 0
    transporter = None  # a medium to allow fields to communicate each other

    if not skip_command:
        # skip_command should be disabled in `non-command` use cases; else ValueError is raised
        # remove "/command@rSophieBot" from message
        text = _remove_command(message)

    if text is None and not allow_missing:
        raise NoArgsGivenError

    if cls.__root_parser__:
        parsed_text = await cls.__root_parser__().get_text(message, text, fields)
    elif text is not None:
        parsed_text = text.split(cls.__splitter__)
    else:
        parsed_text = []  # fallback

    index = len(parsed_text) - 1
    for field, field_info in fields.items():

        # update skipped indexes
        if skipped_indexes and isinstance(field_info.index, int):
            # we dont account slices; as slices is mostly present in last of args?
            # anyway use case for slices are mostly reasons, nobody places such fields at middle
            field_info.index = field_info.index - skipped_indexes
        # check the maximum index needed
        if isinstance(field_info.index, int):
            max_index: typing.Union[int, float] = field_info.index
        elif isinstance(field_info.index, slice):

            if field_info.index.stop:
                max_index = field_info.index.stop
            elif field_info.index.start:
                max_index = field_info.index.start
            else:
                # look like it need all args
                max_index = float('-inf')
                if not parsed_text:
                    # if text is empty; assign any non-zero +ive integer
                    max_index = 1
        else:
            max_index = 0

        if max_index > index:
            if field_info.default is not Undefined:
                values[field] = field_info.default
            elif field_info.allow_none:
                values[field] = None
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
                    args.append(values)

                if parser.communicate:
                    args.append(transporter)

                try:
                    if inspect.iscoroutinefunction(parser.parser):
                        parsed = await parser.parser(cls, *args)
                    else:
                        parsed = parser.parser(cls, *args)
                except (TypeError, ValueError, AssertionError):
                    if field_info.default is not Undefined or field_info.allow_none:
                        value = field_info.default if field_info.default is not Undefined else None  # allow_none
                        # so next fields index should be reduced
                        skipped_indexes += 1
                    else:
                        # skip parsing
                        raise SkipParsing
                else:
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


def _remove_command(message: Message) -> typing.Optional[str]:
    # check whether text's first word is a command
    # why message.text ? caption doesnt count as a command text, whatever!
    if message.text is not None:
        if message.text.startswith("/"):
            cmd_text = message.text.split(maxsplit=1)
            if len(cmd_text) == 1:
                # seems empty args
                return None
            else:
                return cmd_text[-1]
    raise ValueError("Message should not be None or must contain command at offset 0")
