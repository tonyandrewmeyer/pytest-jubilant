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
    # Run the log action successfully — the action returns only once all
    # `juju-log` calls have completed, so Juju has already ingested the log
    # lines by the time we trigger the failure below. Failing the action itself
    # would race the model teardown against Juju's server-side log ingestion,
    # and some of the last lines were regularly missing from the dump (#58).
    foo.run("log/0", "log")
    pytest.fail("Failing on purpose for tests.")
