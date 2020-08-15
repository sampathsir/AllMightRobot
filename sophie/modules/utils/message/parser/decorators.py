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

from .parser import _parse
from ._internal import _Parser
from .errors import NoArgsGivenError, SkipParsing, MissingField, NoParserGivenError

if typing.TYPE_CHECKING:
    from aiogram.api.types import Message
    from .bases import ArgumentParser


def parse_method(
        *fields: str, last_fields: bool = False, pass_whole_text: bool = False, communicate: bool = False
) -> typing.Callable[[typing.Callable[..., typing.Any]], classmethod]:

    """
    Decorator for assigning methods to field parsers

    You can use the decorator as follows::

        @parse_method("field1", "field2")
        async def field_one_method(cls, message, text):
            # yes! parse methods can be async
            # text param returns the IndexField matched text
            return text, {"I got field1", 1}

    You could also communicate between fields, to receieve comm data, you should use ``communication=True`` param::

        @parse_method("field3", communicate=True)
        def field3_parse_method(cls, message, text, communication):
            # communication param contains "{"I got field1": 1}
            return text

    You can also view the value of last fields::

        @parse_method("field4", last_fields=True, communication=True)
        def field4_parse_method(cls, message, text, last_fields, comm):
            # last_fields :> {"field1": ..., "field2": ...}
            return text


    :param fields:  fields which parser made for
    :param last_fields: If True, parser will get all parsed fields (yet)
    :param pass_whole_text: whole text instead of Index matched field
    :param communicate:  if parser need to recieve additional data from last field
    """

    def decorator(func: typing.Callable[..., typing.Any]) -> classmethod:
        f_cls = func if isinstance(func, classmethod) else classmethod(func)
        setattr(  # noqa
            f_cls,
            "__parser_method__",
            (
                fields,
                _Parser(f_cls.__func__, last_fields, pass_whole_text, communicate)
            )
        )
        return f_cls
    return decorator


def parse_arguments(
        parser: typing.Optional[typing.Type[ArgumentParser]] = None,
        allow_missing: bool = False,
        skip_command: bool = False
) -> typing.Callable[[typing.Callable[..., typing.Any]], typing.Any]:
    """
    Use this decorator on your `class`

    **Usage:**
        *first method* : you can declare model of your arguments at first::

            args: SomeName # for type hint

            class SomeName(ArgumentParser):
                ...

            @parse_argument(SomeName)
            class Handler(..Handler):
                pass

        *Second method* : declaring model as inner class inside the handler::

            # when having multiple decs; it's prefered to be at bottom
            @parse_arguments()
            class Handler(MessageHandler):
                class Arguments:  # it's not necessary to inherit "ArgumentParser"
                    # note: class name should "Arguments"
                    arg1: int = ArgField(...)
        .

    You could also inherit pre defined `Arguments` class to include it's parsers, field and you can override.

    **NOTE** Creating mutiple parser for one field doesnt work, the last parser that would be
    defined, accounted as the `actual` parser

    :param parser: the defined parser of this handler (should be type of 'ArgumentParser')
    :param allow_missing: to continue even no arguments given, defaults to 'False'; this is NOT for fields!
    :param skip_command: if you want to include bot command (/command@UserBot) as args (doesnt work on `captions`)
    """

    def decorator(
            func: typing.Callable[..., typing.Any]
    ) -> typing.Callable[..., typing.Any]:

        async def wrapped(event: Message, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            cls = parser
            if cls is None:
                if possible_parser := getattr(func, "Arguments", None):
                    cls = possible_parser
                else:
                    # no parser is given
                    raise NoParserGivenError(f"Can't find any arg parser for {func.__name__}")

            try:
                text = event.text or event.caption
                arguments = await _parse(cls, event, text, allow_missing, skip_command)

            except NoArgsGivenError:
                text = "Not enough arghs! Read help for more info"  # TODO: button, and localize these strings
                return await event.reply(text)

            except MissingField as error:
                text = f"Not enough arghs! missing argument '{error.field_name}'"
                if error.field_info.description:  # TODO: localize
                    text += f" ({error.field_info.description})"
                return await event.reply(text)

            except SkipParsing:
                # this error is called to skip parsing
                pass
            else:
                return await func(event, *args, arguments=arguments, **kwargs)
        return wrapped
    return decorator
