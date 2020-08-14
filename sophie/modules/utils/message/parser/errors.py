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
    from ._internal import _ArgField


class MissingField(Exception):
    def __init__(self, field_name: str, field_info: _ArgField):
        self.field_name = field_name
        self.field_info = field_info


class NoArgsGivenError(Exception):
    pass


class SkipParsing(Exception):
    """
    Allows you to skip parsing (note: this would cancel the handler)
    """
    pass


class MultipleFieldParserError(Exception):
    pass


class NoParserGivenError(Exception):
    pass
