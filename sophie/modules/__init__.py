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

import os

from typing import Any, List, Union, Optional

from aiogram import Router
from sophie.utils.logging import log


class BaseModule:

    router: Optional[Union[List[Router], Router]]
    """Registered router(s) for the module"""

    priority: Union[int, float] = float('inf')
    """Priority of the module, if Zero (0), module will reach the updates first, defaults to inf"""

    async def __setup__(*args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Setup function is not Implemented for this function!")


def get_registered_modules() -> List:
    return BaseModule.__subclasses__()


def list_all_modules() -> list:
    modules_directory = 'sophie/modules'

    all_modules = []
    for directory in os.listdir(modules_directory):
        path = modules_directory + '/' + directory
        if not os.path.isdir(path):
            continue

        if directory == '__pycache__':
            continue

        if not os.path.isfile(path + '/version.txt'):
            continue

        if directory in all_modules:
            log.critical("Modules with same name can't exists!")
            exit(5)

        all_modules.append(directory)
    return all_modules


ALL_MODULES: list = sorted(list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]
