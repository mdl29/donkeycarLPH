# coding: utf-8

# Copyright (C) 2017 Open Path View, Maison Du Libre
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

# Contributors: Benjamin BERNARD <benjamin.bernard@openpathview.fr>
# Email: team@openpathview.fr
# Description: Helps to configure logger.

# Best practices for loggers :
# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

import os
import logging.config

import yaml

DEFAULT_LOGGING_CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/../config/logging.yaml"
DEFAULT_LOGGING_LEVEL = logging.INFO
DEFAULT_LOGGING_ENV_NAME = 'LOG_CFG'


def setup_logging(
        default_path: str = DEFAULT_LOGGING_CONFIG_PATH,
        default_level: str = DEFAULT_LOGGING_LEVEL,
        env_key: str = DEFAULT_LOGGING_ENV_NAME):
    """
    Setup logging configuration.
    :param default_path: Path of the logging yaml configuration file (optional)
    :param default_level: Default logger level.
    :param env_key: Environment variable name where the path to the configuration file is set.
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = os.path.realpath(value)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
