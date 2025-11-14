"""Basic sanity checks for the test harness.

This module contains minimal assertions to verify that the testing setup
is functional. It serves as a quick smoke test to ensure the test runner
and environment are configured correctly.
"""


def test_sanity():
    """Verify arithmetic as a trivial smoke test."""
    assert 1 + 1 == 2
