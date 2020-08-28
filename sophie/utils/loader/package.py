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

from importlib import import_module
from pathlib import Path
from typing import List, Union, cast

from aiogram import Router

from sophie.modules import BaseModule
from sophie.utils.logging import log
from .requirements import check_requirements

from sophie.utils.config import real_config, config


class Package:
    routers: List[Router]
    p_object: BaseModule
    version: Union[str, None] = None

    def __init__(self, type: str, name: str, path: Path):  # noqa: A002
        self.type = type
        self.name = name
        self.path = path
        self.python_path = str(self.path).replace('/', '.')

        if not path.exists():
            raise FileNotFoundError

        log.debug(f"Loading {self.name} package, {self.type=}...")

        if (requirements_file_path := self.path / 'requirements.txt').exists():
            log.debug(f"Checking requirements for {self.name} {self.type}...")
            with open(requirements_file_path) as f:
                check_requirements(f)
                log.debug("...Done!")

        log.debug(f"Importing {self.name} package...")
        self.p_object: BaseModule = cast(BaseModule, import_module(self.python_path))

        version_file = self.path / 'version.txt'
        if version_file.exists():
            with open(version_file) as f:
                self.version = f.read()

        if hasattr(self.p_object, '__config__'):
            log.debug(f"Setting config for {self.name} package")
            setattr(getattr(config, self.type), self.name, self.p_object.__config__().parse_obj(
                real_config[self.type][self.name] if self.name in real_config[self.type] else {}
            ))

        if hasattr(self.p_object, '__pre_init__'):
            log.debug(f"Running __pre_init__ of {self.name} package...")
            self.p_object.__pre_init__(self)
            log.debug("...Done")

        if self.type == 'module':
            self._load_module()

        log.debug("...Done!")

    def _load_module(self) -> None:
        from sophie.services.aiogram import modules_router

        self.module = self.p_object

        # Load routers
        if self.module.router:

            log.debug(f"Loading router(s) for {self.name} {self.type}...")
            if not isinstance(self.module.router, list):
                self.routers = [self.module.router]
            self.routers = self.routers

            # Include routers
            for router in self.routers:
                modules_router.include_router(router)
            log.debug("...Done")
