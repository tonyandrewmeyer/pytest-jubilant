"""This file is executed via test_dump_logs.py, it should not be run directly."""

from __future__ import annotations

import typing

import jubilant
import pytest

if typing.TYPE_CHECKING:
    import pathlib

    import pytest_jubilant


@pytest.fixture(scope="module")
def models(juju_factory: pytest_jubilant.JujuFactory):
    foo = juju_factory.get_juju("foo1")
    bar = juju_factory.get_juju("bar1")
    yield foo, bar


@pytest.mark.juju_setup
def test_deploy_and_then_fail(
    log_actions_charm: pathlib.Path, models: tuple[jubilant.Juju, jubilant.Juju]
):
    foo, bar = models
    foo.deploy(log_actions_charm, app="log")
    bar.deploy(log_actions_charm, app="log")
    foo.wait(jubilant.all_active, timeout=900)
    bar.wait(jubilant.all_active)
    # Don't use the action's own "fail" parameter: the action failing races with
    # Juju finishing ingestion of the 10k log lines, so the last of them are
    # regularly missing from the dump. Letting the action return means every line
    # has been accepted before we fail the test ourselves. See #58.
    foo.run("log/0", "log")
    pytest.fail("Failing on purpose for tests.")
