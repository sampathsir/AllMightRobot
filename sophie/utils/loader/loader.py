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

import asyncio
from typing import ValuesView, Any

from sophie.modules.utils.filters import __setup__ as filters_setup
from sophie.modules.utils.middlewares import __setup__ as middlewares_setup
from sophie.utils.logging import log
from .modules import load_all_modules


async def before_srv_task(packages: ValuesView[dict]) -> Any:
    for package in [m for m in packages if hasattr(m.p_object, '__setup__')]:
        log.debug(f"Running __setup__ for: {package.name}")
        await package.p_object.__setup__()

    for package in [m for m in packages if hasattr(m.p_object, '__before_serving__')]:
        log.debug(f"Running __before_serving__ for: {package.name}")
        await package.p_object.__before_serving__()


def post_init(loop) -> Any:
    from . import LOADED_MODULES
    from . import LOADED_COMPONENTS

    # Run before_srv_task for components
    log.debug("Running before_srv_task for components...")
    loop.run_until_complete(before_srv_task(LOADED_COMPONENTS.values()))
    log.debug("...Done!")

    # Run before_srv_task for modules
    log.debug("Running before_srv_task for modules...")
    loop.run_until_complete(before_srv_task(LOADED_MODULES.values()))
    log.debug("...Done!")


def load_all(loop) -> None:
    log.debug('Loading top-level custom filters...')
    filters_setup()
    log.debug('...Done!')

    log.debug('Loading modules...')
    load_all_modules()
    log.info('Modules loaded successfully!')

    log.debug('Loading middlewares...')
    middlewares_setup()
    log.debug('...Done!')

    log.debug('Running postinit stage...')
    post_init(loop)
    log.debug('...Done!')
