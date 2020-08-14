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

if typing.TYPE_CHECKING:
    from .fields import IndexField


class _ArgField:
    __slots__ = 'default', 'index', 'parser', 'allow_none', 'description'

    def __init__(
            self,
            default: typing.Any,
            index: typing.Union[typing.Type[IndexField], int],
            allow_none: bool,
            description: str = None
    ):
        self.default = default
        self.index = index
        self.allow_none = allow_none
        print(description)
        self.description = description


class _Parser:
    __slots__ = "last_fields", "parser", "whole_text", "communicate"

    def __init__(
            self, parser: typing.Callable[..., typing.Any], last_fields: bool, whole_text: bool, communicate: bool
    ):
        self.parser = parser
        self.last_fields = last_fields
        self.whole_text = whole_text
        self.communicate = communicate
