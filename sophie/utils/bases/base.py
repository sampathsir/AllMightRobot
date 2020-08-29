# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo.
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

from abc import ABC
from typing import Callable, Type, Dict, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from sophie.modules.utils.text import FormatListText

    from pydantic import BaseModel
    from types import ModuleType


class Base(ABC):
    # these maybe populated or maybe not
    if TYPE_CHECKING:
        configurations: Type[BaseModel]
        __pre_init__: Callable[[ModuleType], Any]
        __before_serving__: Callable[..., Any]

    async def __setup__(*args: Any, **kwargs: Any) -> None:
        pass
