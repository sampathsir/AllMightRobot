# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2020 Jeepeo
#
# This file is part of SophieBot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import typing

from motor.motor_asyncio import AsyncIOMotorClient
from motor_odm import Document

from sophie.utils.config import cfg

if typing.TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from motor.core import AgnosticDatabase


def __init_motor__(loop: AbstractEventLoop) -> AgnosticDatabase:
    motor = AsyncIOMotorClient(cfg.mongo.url, io_loop=loop)
    mongo = motor[cfg.mongo.namespace]

    Document.use(mongo)
    return mongo


__all__ = ["Document", "__init_motor__"]
