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

import json
import pathlib
import pytest

from foris_controller_testtools.fixtures import (
    only_message_buses,
    backend,
    infrastructure,
    start_buses,
    mosquitto_test,
    ubusd_test,
    notify_api,
)


@pytest.fixture(scope="function")
def init_snapshots():
    path = pathlib.Path("/tmp/test-schnapps.json")
    with path.open("w") as f:
        json.dump(
            {
                "snapshots": [
                    {
                        "number": 1,
                        "created": "2019-11-27 14:15:27 +0000",
                        "type": "single",
                        "size": "74.16MiB",
                        "description": "ARGGGHHH",
                    },
                    {
                        "number": 2,
                        "created": "2019-11-29 17:18:34 +0000",
                        "type": "single",
                        "size": "63.28MiB",
                        "description": "ARRGGHH 2",
                    },
                ]
            },
            f,
        )

    yield

    path.unlink()


def test_list(infrastructure, start_buses, init_snapshots):
    res = infrastructure.process_message(
        {"module": "schnapps", "action": "list", "kind": "request"}
    )
    assert "error" not in res
    assert "data" in res
    assert "snapshots" in res["data"]


def test_create(infrastructure, start_buses, init_snapshots):
    filters = [("schnapps", "create")]

    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message(
        {
            "module": "schnapps",
            "action": "create",
            "kind": "request",
            "data": {"description": "Testing snapshot 1"},
        }
    )
    assert "number" in res["data"]

    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1]["module"] == "schnapps"
    assert notifications[-1]["action"] == "create"
    assert notifications[-1]["kind"] == "notification"
    assert "number" in notifications[-1]["data"]

    res = infrastructure.process_message(
        {"module": "schnapps", "action": "list", "kind": "request"}
    )
    assert res["data"]["snapshots"][-1]["description"] == "Testing snapshot 1"
    assert res["data"]["snapshots"][-1]["type"] == "single"
    assert "size" in res["data"]["snapshots"][-1]
    assert "number" in res["data"]["snapshots"][-1]
    assert "created" in res["data"]["snapshots"][-1]


def test_delete(infrastructure, start_buses, init_snapshots):
    def create(description: str) -> int:
        return infrastructure.process_message(
            {
                "module": "schnapps",
                "action": "create",
                "kind": "request",
                "data": {"description": description},
            }
        )["data"]["number"]

    first = create("firsttt")
    second = create("seconddd")

    filters = [("schnapps", "delete")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message(
        {"module": "schnapps", "action": "delete", "kind": "request", "data": {"number": first}}
    )
    assert res["data"]["result"]
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        "module": "schnapps",
        "action": "delete",
        "kind": "notification",
        "data": {"number": first},
    }

    snapshots = infrastructure.process_message(
        {"module": "schnapps", "action": "list", "kind": "request"}
    )["data"]["snapshots"]

    ids = [e["number"] for e in snapshots]
    assert first not in ids
    assert second in ids


def test_rollback(infrastructure, start_buses, init_snapshots):
    def create(description: str) -> int:
        return infrastructure.process_message(
            {
                "module": "schnapps",
                "action": "create",
                "kind": "request",
                "data": {"description": description},
            }
        )["data"]["number"]

    first = create("firstttt")
    second = create("secondddd")

    filters = [("schnapps", "rollback")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message(
        {"module": "schnapps", "action": "rollback", "kind": "request", "data": {"number": first}}
    )
    assert res["data"]["result"]
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        "module": "schnapps",
        "action": "rollback",
        "kind": "notification",
        "data": {"number": first, "shifted": [second]},
    }

    snapshots = infrastructure.process_message(
        {"module": "schnapps", "action": "list", "kind": "request"}
    )["data"]["snapshots"]

    ids = [e["number"] for e in snapshots]
    assert first in ids
