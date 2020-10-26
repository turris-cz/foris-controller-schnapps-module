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

import json
import pathlib
import pytest
import textwrap

from foris_controller_testtools.fixtures import (
    only_message_buses,
    backend,
    infrastructure,
    start_buses,
    mosquitto_test,
    ubusd_test,
    notify_api,
    only_backends,
)
from foris_controller_testtools.utils import FileFaker


@pytest.fixture(scope="function")
def mount_cmd_with_btrfs(cmdline_script_root):
    content = """\
        #!/bin/bash
        cat << EOF
        /dev/mmcblk0p1 on / type btrfs (ro,noatime,ssd,space_cache,commit=5,subvolid=1329,subvol=/@)
        devtmpfs on /dev type devtmpfs (rw,relatime,size=513800k,nr_inodes=128450,mode=755)
        proc on /proc type proc (rw,nosuid,nodev,noexec,noatime)
        sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,noatime)
        tmpfs on /tmp type tmpfs (rw,nosuid,nodev,noatime)
        tmpfs on /dev type tmpfs (rw,nosuid,relatime,size=512k,mode=755)
        devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,mode=600,ptmxmode=000)
        /dev/sda on /srv type btrfs (rw,noatime,space_cache,subvolid=257,subvol=/@)
        EOF"""

    with FileFaker(cmdline_script_root, "/usr/bin/mount", True, textwrap.dedent(content)) as f:

        yield f


@pytest.fixture(scope="function")
def mount_cmd_with_nobtrfs(cmdline_script_root):
    content = """\
        #!/bin/bash
        cat << EOF
        /dev/mmcblk0p1 on / type ext4 (ro,noatime,ssd,space_cache,commit=5,subvolid=1329,subvol=/@)
        devtmpfs on /dev type devtmpfs (rw,relatime,size=513800k,nr_inodes=128450,mode=755)
        proc on /proc type proc (rw,nosuid,nodev,noexec,noatime)
        sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,noatime)
        tmpfs on /tmp type tmpfs (rw,nosuid,nodev,noatime)
        tmpfs on /dev type tmpfs (rw,nosuid,relatime,size=512k,mode=755)
        devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,mode=600,ptmxmode=000)
        /dev/sda on /srv type btrfs (rw,noatime,space_cache,subvolid=257,subvol=/@)
        EOF"""

    with FileFaker(cmdline_script_root, "/usr/bin/mount", True, textwrap.dedent(content)) as f:

        yield f


@pytest.fixture(scope="function")
def init_snapshots():
    path = pathlib.Path("/tmp/test-schnapps.json")
    with path.open("w") as f:
        json.dump(
            {
                "snapshots": [
                    {
                        "number": 1,
                        "created": "2019-11-21 14:15:27 +0000",
                        "type": "pre",
                        "size": "61.16MiB",
                        "description": "ARGGGHHH",
                    },
                    {
                        "number": 2,
                        "created": "2019-11-22 17:18:34 +0000",
                        "type": "post",
                        "size": "62.28MiB",
                        "description": "ARRGGHH 2",
                    },
                    {
                        "number": 3,
                        "created": "2019-11-23 17:18:34 +0000",
                        "type": "time",
                        "size": "63.12MiB",
                        "description": "ARRGGHH 3",
                    },
                    {
                        "number": 4,
                        "created": "2019-11-24 17:18:34 +0000",
                        "type": "single",
                        "size": "64.12MiB",
                        "description": "ARRGGHH 4",
                    },
                    {
                        "number": 5,
                        "created": "2019-11-25 17:18:34 +0000",
                        "type": "rollback",
                        "size": "65.12MiB",
                        "description": "ARRGGHH 5",
                    },
                ]
            },
            f,
        )
    yield
    path.unlink()


@pytest.fixture(scope="function")
def init_snapshots_bad_description():
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
                        "description": "A"*1025,
                    }
                ]
            },
            f,
        )
    yield
    path.unlink()


def test_list(infrastructure, start_buses, init_snapshots, mount_cmd_with_btrfs):
    res = infrastructure.process_message(
        {"module": "schnapps", "action": "list", "kind": "request"}
    )
    assert "error" not in res
    assert "data" in res
    assert "snapshots" in res["data"]


@pytest.mark.only_backends(["openwrt"])
def test_list_error(infrastructure, start_buses, init_snapshots_bad_description, mount_cmd_with_btrfs):
    res = infrastructure.process_message(
        {"module": "schnapps", "action": "list", "kind": "request"}
    )
    assert "maxLength" in res["errors"][0]["stacktrace"]


def test_create(infrastructure, start_buses, init_snapshots, mount_cmd_with_btrfs):
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


def test_delete(infrastructure, start_buses, init_snapshots, mount_cmd_with_btrfs):
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


def test_rollback(infrastructure, start_buses, init_snapshots, mount_cmd_with_btrfs):
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


@pytest.mark.only_backends(["openwrt"])
def test_list_nobtrfs(infrastructure, start_buses, init_snapshots, mount_cmd_with_nobtrfs):
    assert (
        len(
            infrastructure.process_message(
                {"module": "schnapps", "action": "list", "kind": "request"}
            )["data"]["snapshots"]
        )
        == 0
    )


@pytest.mark.only_backends(["openwrt"])
def test_create_nobtrfs(infrastructure, start_buses, init_snapshots, mount_cmd_with_nobtrfs):
    assert (
        infrastructure.process_message(
            {
                "module": "schnapps",
                "action": "create",
                "kind": "request",
                "data": {"description": "should not happen"},
            }
        )["data"]["result"]
        is False
    )


@pytest.mark.only_backends(["openwrt"])
def test_delete_nobtrfs(infrastructure, start_buses, init_snapshots, mount_cmd_with_nobtrfs):
    assert (
        infrastructure.process_message(
            {"module": "schnapps", "action": "delete", "kind": "request", "data": {"number": 1}}
        )["data"]["result"]
        is False
    )


@pytest.mark.only_backends(["openwrt"])
def test_rollback_nobtrfs(infrastructure, start_buses, init_snapshots, mount_cmd_with_nobtrfs):
    assert (
        infrastructure.process_message(
            {"module": "schnapps", "action": "rollback", "kind": "request", "data": {"number": 1}}
        )["data"]["result"]
        is False
    )

def test_factory_reset_btrfs(infrastructure, init_snapshots, mount_cmd_with_btrfs):
    res =  infrastructure.process_message(
        {"module": "schnapps", "action": "factory_reset", "kind": "request"}
    )
    assert "errors" not in res.keys()
    assert res["data"]["result"]

@pytest.mark.only_backends(["openwrt"])
def test_factory_reset_nobtrfs(infrastructure, init_snapshots, mount_cmd_with_nobtrfs):
    res = infrastructure.process_message(
        {"module": "schnapps", "action": "factory_reset", "kind": "request"}
    )
    assert "errors" not in res.keys()
    assert res["data"]["result"] is False
