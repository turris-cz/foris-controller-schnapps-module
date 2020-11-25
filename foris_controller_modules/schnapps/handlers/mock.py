#
# foris-controller-schnapps-module
# Copyright (C) 2019-2020 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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

import datetime
import logging
import typing
import random

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockSchnappsHandler(Handler, BaseMockHandler):
    idx = 0

    snapshots: typing.List[dict] = []

    @logger_wrapper(logger)
    def list(self) -> dict:
        return {"snapshots": MockSchnappsHandler.snapshots}

    @logger_wrapper(logger)
    def create(self, description: str) -> typing.Optional[int]:
        MockSchnappsHandler.idx += 1
        MockSchnappsHandler.snapshots.append(
            {
                "number": MockSchnappsHandler.idx,
                "created": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S +0000"),
                "type": "single",
                "size": f"{random.randint(1, 100000) / 100}MiB",
                "description": description,
            }
        )
        return MockSchnappsHandler.idx

    @logger_wrapper(logger)
    def delete(self, number: int) -> bool:
        ids = [e["number"] for e in MockSchnappsHandler.snapshots]
        if number not in ids:
            return False
        MockSchnappsHandler.snapshots = [
            e for e in MockSchnappsHandler.snapshots if e["number"] != number
        ]
        return True

    @logger_wrapper(logger)
    def rollback(self, number: int) -> typing.Tuple[bool, typing.Optional[typing.List[int]]]:
        ids = [e["number"] for e in MockSchnappsHandler.snapshots]
        if number not in ids:
            return False, None
        return True, [e["number"] for e in MockSchnappsHandler.snapshots if e["number"] > number]

    @logger_wrapper(logger)
    def factory_reset(self) -> bool:
        return True
