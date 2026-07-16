import pytest

from pytest_jubilant._main import _juju_arch


@pytest.mark.parametrize(
    ("machine", "expected"),
    [
        ("x86_64", "amd64"),
        ("X86_64", "amd64"),  # platform.machine() casing varies by platform.
        ("amd64", "amd64"),
        ("aarch64", "arm64"),
        ("arm64", "arm64"),
        ("ppc64le", "ppc64el"),
        ("s390x", "s390x"),
        ("riscv64", "riscv64"),
        ("something-unknown", "something-unknown"),  # Unknown names pass through unchanged.
    ],
)
def test_juju_arch_mapping(monkeypatch: pytest.MonkeyPatch, machine: str, expected: str):
    """``_juju_arch`` maps platform.machine() names to the names Juju uses."""
    monkeypatch.setattr("platform.machine", lambda: machine)
    assert _juju_arch() == expected
