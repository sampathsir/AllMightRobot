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

import os
import inspect

from importlib import import_module
from types import ModuleType
from typing import List, Dict, Union, Any

from aiogram import Router
from sophie.utils.logging import log
from sophie.utils.config import config

from .requirements import check_requirements


class LoadPackage:
    routers: Dict[Router, Union[float, int]] = {}

    def load_pkg(self, pkg: dict) -> dict:
        # Stage 1 - check requirements and load components
        requirements_file_path = f"{pkg['path']}/requirements.txt"
        if os.path.exists(requirements_file_path):
            with open(requirements_file_path) as f:
                log.debug(f"Checking requirements for {pkg['name']} {pkg['type']}...")
                check_requirements(f)
                log.debug("...Passed!")

        log.debug(f"Importing <d><n>{pkg['name']}</></> {pkg['type']}")
        imported_module = import_module(pkg['package_path'])

        pkg['object'] = imported_module
        # get version
        self.get_version(imported_module, pkg)
        if pkg['type'] == 'module':
            self.get_module_info(imported_module, pkg)
        return pkg

    def get_module_info(self, module: ModuleType, pkg: dict) -> Any:
        from sophie.modules import get_registered_modules, BaseModule

        obj: BaseModule
        for _, obj in inspect.getmembers(module, predicate=lambda value: value in get_registered_modules()):

            pkg['object'] = obj
            if obj.router:
                pkg['router'] = obj.router

                log.debug(f"Loading router(s) for {pkg['name']} {pkg['type']}")
                if isinstance(obj.router, list):
                    for router in obj.router:
                        self.routers[router] = obj.priority
                else:
                    self.routers[obj.router] = obj.priority

    def load_routers(self) -> Any:
        from sophie.services.aiogram import dp

        routers = self.get_sorted_list()
        for router in routers:
            dp.include_router(router)

    def get_sorted_list(self) -> List[Router]:
        def sort(value: Any) -> Union[int, float]:
            for router, priority in self.routers.items():
                if value == router:
                    return priority
            raise ValueError("Unexpected value was given")

        return sorted(self.routers, key=sort)

    @staticmethod
    def get_version(module: ModuleType, pkg: dict) -> Any:
        path = str(module.__path__[0])  # type: ignore  # mypy issue #1422
        with open(f"{path}/version.txt") as f:
            version = f.read()
        pkg['version'] = version

    def __call__(self, package: dict) -> dict:
        return self.load_pkg(package)


def load_modules(to_load: List[str]) -> list:
    from . import LOADED_MODULES

    modules: list = []
    loader = LoadPackage()
    for module_name in to_load:
        module = loader(
            {
                "type": "module",
                "name": module_name,
                "path": f"sophie/modules/{module_name}",
                "package_path": f"sophie.modules.{module_name}",
            }
        )
        LOADED_MODULES[module_name] = module
        modules.append(module)

    loader.load_routers()
    log.debug("Registered all routers")

    return modules


def load_all_modules() -> list:
    from sophie.modules import ALL_MODULES

    load = config.modules.load
    dont_load = config.modules.dont_load

    if len(load) > 0:
        to_load = load
    else:
        to_load = ALL_MODULES

    to_load = [x for x in to_load if x not in dont_load]
    log.info("Modules to load: %s", str(to_load))
    load_modules(to_load)

    return to_load
