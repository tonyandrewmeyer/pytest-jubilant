"""This file is executed via test_cli_skip_on_failure.py, it should not be run directly."""

import jubilant
import pytest


@pytest.mark.juju_setup
def test_setup_fails(juju: jubilant.Juju):
    raise AssertionError("setup intentionally fails")


def test_regular_should_be_skipped(juju: jubilant.Juju):
    raise AssertionError("this test should be skipped, not run")


@pytest.mark.juju_teardown
def test_teardown_should_be_skipped(juju: jubilant.Juju):
    raise AssertionError("this teardown should be skipped, not run")
