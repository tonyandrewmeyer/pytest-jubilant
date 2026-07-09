from pathlib import Path

pytest_plugins = ["pytester"]

CONFTEST = (Path(__file__).parent / "conftest.py").read_text()
TEST_FILE = """
def test_use_factory(juju_factory):
    juju_factory.get_juju("foo")
    juju_factory.get_juju("bar")
""".strip()


def test_dump_logs_not_passed(pytester):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_file=TEST_FILE)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    assert not (pytester.path / ".logs").exists()


def test_dump_logs_empty_path_disables(pytester):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_file=TEST_FILE)

    result = pytester.runpytest("--juju-dump-logs", "")
    result.assert_outcomes(passed=1)

    assert not (pytester.path / ".logs").exists()


def test_dump_logs_default_path(pytester):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_file=TEST_FILE)

    result = pytester.runpytest("--juju-dump-logs")
    result.assert_outcomes(passed=1)

    foo_log_path = pytester.path / ".logs" / "jubilant-deadbeef-test-file-foo-juju-debug.log"
    assert foo_log_path.exists()
    assert foo_log_path.read_text() == "stdout patched by conftest.py"
    bar_log_path = pytester.path / ".logs" / "jubilant-deadbeef-test-file-bar-juju-debug.log"
    assert bar_log_path.exists()
    assert bar_log_path.read_text() == "stdout patched by conftest.py"


def test_dump_logs_custom_path(pytester, tmp_path):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_file=TEST_FILE)
    custom_dir = tmp_path / "custom-logs"

    result = pytester.runpytest("--juju-dump-logs", str(custom_dir))
    result.assert_outcomes(passed=1)

    foo_log_path = custom_dir / "jubilant-deadbeef-test-file-foo-juju-debug.log"
    assert foo_log_path.exists()
    assert foo_log_path.read_text() == "stdout patched by conftest.py"
    bar_log_path = custom_dir / "jubilant-deadbeef-test-file-bar-juju-debug.log"
    assert bar_log_path.exists()
    assert bar_log_path.read_text() == "stdout patched by conftest.py"


TEST_FILE_LOGS = """
import logging

def test_emit_log(juju_factory):
    juju_factory.get_juju("foo")
    logging.getLogger("jubilant").info("hello from a test")
""".strip()


def test_dump_logs_captures_jubilant_log(pytester, tmp_path):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_file=TEST_FILE_LOGS)
    custom_dir = tmp_path / "custom-logs"

    result = pytester.runpytest("--juju-dump-logs", str(custom_dir))
    result.assert_outcomes(passed=1)

    jubilant_log_path = custom_dir / "jubilant.log"
    assert jubilant_log_path.exists()
    assert "hello from a test" in jubilant_log_path.read_text()


def test_dump_logs_not_passed_no_jubilant_log(pytester):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(test_file=TEST_FILE_LOGS)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    assert not (pytester.path / ".logs" / "jubilant.log").exists()


def test_juju_debug_log_on_failure(pytester, tmp_path):
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(
        test_file="""
def test_fail(juju_factory):
    juju_factory.get_juju("foo")
    assert False
"""
    )
    custom_dir = tmp_path / "custom-logs"

    result = pytester.runpytest_subprocess(
        "--juju-model", "model-t", "--juju-dump-logs", str(custom_dir)
    )

    # We expect this session to fail.
    result.assert_outcomes(failed=1)

    # We emit the last 1000 lines of `juju debug-log` for each model if tests fail.
    foo_msg = "Logging last 1000 lines of `juju debug-log` for model model-t-test-file-foo:"
    foo_lines = result.stdout.get_lines_after(f"*{foo_msg}*")  # Match with fnmatch.
    assert foo_lines[0] == "stdout patched by conftest.py"  # Mocked call to Juju CLI.
    assert foo_lines[1] == "--- end of `juju debug-log` for model model-t-test-file-foo ---"

    # The full logs are still written on failure with --dump-logs.
    foo_log_path = custom_dir / "model-t-test-file-foo-juju-debug.log"
    assert foo_log_path.exists()
