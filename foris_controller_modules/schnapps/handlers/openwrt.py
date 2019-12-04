#
# foris-controller-schnapps-module
# Copyright (C) 2019 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import logging
import typing

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.schnapps import SchnappsCmds

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtSchnappsHandler(Handler, BaseOpenwrtHandler):

    cmds = SchnappsCmds()

    @logger_wrapper(logger)
    def list(self) -> dict:
        return OpenwrtSchnappsHandler.cmds.list()

    @logger_wrapper(logger)
    def create(self, description: str) -> typing.Optional[int]:
        return OpenwrtSchnappsHandler.cmds.create(description)

    @logger_wrapper(logger)
    def delete(self, number: int) -> bool:
        return OpenwrtSchnappsHandler.cmds.delete(number)

    @logger_wrapper(logger)
    def rollback(self, number: int) -> typing.Tuple[bool, typing.Optional[typing.List[int]]]:
        return OpenwrtSchnappsHandler.cmds.rollback(number)
