"""Shared pytest configuration."""

from __future__ import annotations


def pytest_addoption(parser):
    parser.addoption(
        "--run-cli",
        action="store_true",
        default=False,
        help="Run quarantined legacy CLI tests (post-ADR-006).",
    )
