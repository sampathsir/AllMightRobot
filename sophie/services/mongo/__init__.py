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

from pymongo.errors import ServerSelectionTimeoutError

from .mongo import sync_mongo, mongo_client
from .motor import __init_motor__, Document
from sophie.utils.logging import log

if typing.TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from motor.core import AgnosticDatabase

mongo: AgnosticDatabase = None  # noqa  # to be populated


def __setup__(loop: AbstractEventLoop) -> typing.Any:
    global mongo
    mongo = __init_motor__(loop)

    try:
        mongo_client.server_info()
    except ServerSelectionTimeoutError:
        log.critical("Can't connect to the MongoDB! Exiting...")
        exit(2)


__all__ = ["mongo", "sync_mongo", "Document", "__setup__"]
