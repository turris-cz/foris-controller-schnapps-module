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

import logging

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class SchnappsModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_list(self, data: dict) -> dict:
        return self.handler.list()

    def action_create(self, data: dict) -> dict:
        number = self.handler.create(**data)
        if number is not None:
            self.notify("create", {"number": number})
            return {"number": number, "result": True}
        return {"result": False}

    def action_delete(self, data: dict) -> dict:
        res = self.handler.delete(**data)
        if res:
            self.notify("delete", data)
        return {"result": res}

    def action_rollback(self, data: dict) -> dict:
        res, shifted = self.handler.rollback(**data)
        response = {"result": res}
        if res:
            self.notify("rollback", {"number": data["number"], "shifted": shifted})
            response["shifted"] = shifted
        return response

    def action_factory_reset(self, data: dict) -> dict:
        res = self.handler.factory_reset()
        return {"result": res}


@wrap_required_functions(["list", "create", "delete", "rollback", "factory_reset"])
class Handler(object):
    pass
