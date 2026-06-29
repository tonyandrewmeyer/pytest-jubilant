from pathlib import Path

import pytest

pytest_plugins = ["pytester"]

BASE_CONFTEST = (Path(__file__).parent / "conftest.py").read_text()
EXTRA_CONFTEST = (
    BASE_CONFTEST
    + '''


@pytest.fixture(scope="session", autouse=True)
def _patch_model_operations():
    """Mock add_model / destroy_model so the juju fixture doesn't touch a real Juju."""
    import jubilant
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(jubilant.Juju, "add_model", lambda *a, **kw: None)
        monkeypatch.setattr(jubilant.Juju, "destroy_model", lambda *a, **kw: None)
        yield
'''
)

FAILING_FILE = (Path(__file__).parent / "cli_skip_on_failure_tests.py").read_text()
PASSING_FILE = (Path(__file__).parent / "cli_skip_on_failure_isolated_tests.py").read_text()


def test_default_runs_all(pytester: pytest.Pytester):
    """Without --juju-skip-on-failure, a juju_setup failure does not skip the rest."""
    pytester.makeconftest(EXTRA_CONFTEST)
    pytester.makepyfile(test_file=FAILING_FILE)

    result = pytester.runpytest()

    # All three tests raise, so all three fail.
    result.assert_outcomes(failed=3)


def test_skip_on_failure_skips_rest_of_module(pytester: pytest.Pytester):
    """--juju-skip-on-failure: a juju_setup failure skips the rest of the module."""
    pytester.makeconftest(EXTRA_CONFTEST)
    pytester.makepyfile(test_file=FAILING_FILE)

    result = pytester.runpytest("--juju-skip-on-failure")

    # The juju_setup test fails; the other two are skipped.
    result.assert_outcomes(failed=1, skipped=2)


def test_skip_on_failure_no_failure(pytester: pytest.Pytester):
    """--juju-skip-on-failure has no effect when no juju_setup test fails."""
    pytester.makeconftest(EXTRA_CONFTEST)
    pytester.makepyfile(test_file=PASSING_FILE)

    result = pytester.runpytest("--juju-skip-on-failure")

    result.assert_outcomes(passed=2)


def test_skip_on_failure_other_module_unaffected(pytester: pytest.Pytester):
    """A juju_setup failure in one module doesn't affect a different module."""
    pytester.makeconftest(EXTRA_CONFTEST)
    pytester.makepyfile(test_failing=FAILING_FILE, test_passing=PASSING_FILE)

    result = pytester.runpytest("--juju-skip-on-failure")

    # test_failing: 1 failed setup + 2 skipped; test_passing: 2 passed.
    result.assert_outcomes(passed=2, failed=1, skipped=2)
