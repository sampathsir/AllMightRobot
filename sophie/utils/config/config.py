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
#

import json

from pydantic import BaseSettings

from .general import (
    GeneralConfig,
    AdvancedConfig,
    ModuleConfig,
    ComponentConfig,
    MongoConfig,
)


class Conf(BaseSettings):
    # Some fields are required, some can follow default value
    general = GeneralConfig()
    advanced = AdvancedConfig()
    module = ModuleConfig()
    component = ComponentConfig()
    mongo = MongoConfig()


with open('config/config.json') as f:
    real_config = json.load(f)

cfg = Conf.parse_obj(real_config)

__all__ = ["cfg"]
