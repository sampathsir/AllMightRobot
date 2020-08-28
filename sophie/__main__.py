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

import asyncio
from logging import DEBUG

from sophie.services.aiogram import dp, bot
from sophie.services.mongo import __setup__ as init_mongo
from sophie.utils.logging import log
from sophie.utils.config import config

from sophie.utils.loader import load_all

if config.advanced.debug:
    log.setLevel(DEBUG)
    log.warning("! Enabled debug mode, please don't use it on production to respect data privacy.")

loop = asyncio.get_event_loop()


log.debug("Loading database...")
init_mongo(loop)
log.debug("...Done")

load_all(loop)

if config.advanced.migrator:
    from sophie.utils.migrator.migrator import __setup__ as migrator

    log.info("Checking database migration status...")
    loop.run_until_complete(migrator())
    log.info('...Done!')

log.info('Running the bot...')
loop.run_until_complete(dp.start_polling(bot))
