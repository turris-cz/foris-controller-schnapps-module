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
import json
import re
import typing

from foris_controller_backends.cmdline import BaseCmdLine

logger = logging.getLogger(__name__)


class SchnappsCmds(BaseCmdLine):
    def list(self) -> dict:
        stdout, _ = self._run_command_and_check_retval(["/usr/bin/schnapps", "list", "-j"], 0)
        return json.loads(stdout.strip())

    def create(self, description: str) -> int:
        stdout, _ = self._run_command_and_check_retval(
            ["/usr/bin/schnapps", "create", "-t", "single", description], 0
        )
        res = re.match(r"Snapshot number (\d+) created", stdout.decode().strip())
        return int(res.group(1))

    def delete(self, number: int) -> bool:
        ret, _, _ = self._run_command("/usr/bin/schnapps", "delete", str(number))
        return ret == 0

    def rollback(self, number: int) -> typing.Tuple[bool, typing.Optional[typing.List[int]]]:
        snapshots = self.list()["snapshots"]
        ret, _, _ = self._run_command("/usr/bin/schnapps", "rollback", str(number))
        self._run_command("/usr/bin/maintain-reboot-needed")  # best effort
        if ret == 0:
            return True, [e["number"] for e in snapshots if e["number"] > number]

        return False, None
