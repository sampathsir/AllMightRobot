# Copyright (C) 2018 - 2020 MrYacha.
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

import typing

from pydantic import Field
from pymongo import IndexModel, ASCENDING, ReturnDocument

from sophie.services.mongo import sync_mongo, Document
from sophie.utils.logging import log

col_name = 'locale'


class LocalizationDB(Document):
    chat_id: int
    locale_code: str = Field(..., regex=r"^[a-z]{2}-[A-Z]{2}$")

    class Mongo:
        collection = col_name
        indexes = [IndexModel([("chat_id", ASCENDING)], name="chat_id", unique=True)]


async def set_lang(chat_id: int, locale_code: str) -> typing.Optional[LocalizationDB]:
    payload = {
        'chat_id': chat_id,
        'locale_code': locale_code
    }
    data = await LocalizationDB.find_one_and_replace(
        {"chat_id": chat_id}, payload, return_document=ReturnDocument.AFTER, upsert=True
    )
    return data


async def get_lang(chat_id: int) -> typing.Optional[LocalizationDB]:
    data = await LocalizationDB.find_one({"chat_id": chat_id})
    return data


async def __setup__() -> typing.Any:
    if col_name not in sync_mongo.list_collection_names():
        log.info(f'Created not exited column "{col_name}"')
        sync_mongo.create_collection(col_name)

    log.debug(f'Creating indexes for "{col_name}" column')
    await LocalizationDB.init_indexes()
