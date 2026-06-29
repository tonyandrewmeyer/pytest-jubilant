"""This file is executed via test_cli_skip_on_failure.py, it should not be run directly."""

import jubilant
import pytest


@pytest.mark.juju_setup
def test_setup_ok(juju: jubilant.Juju):
    assert juju is not None


def test_regular(juju: jubilant.Juju):
    assert juju is not None
