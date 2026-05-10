"""Smoke tests for the CLI shell (US-08 wiring)."""

from __future__ import annotations

import io
from pathlib import Path

from astranotes.cli import app as cli_app


def _run_with_inputs(inputs: list[str], monkeypatch, tmp_path: Path) -> str:
    monkeypatch.setenv("ASTRANOTES_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ASTRANOTES_KEY", cli_app.PrivacyService.generate_key().decode())
    out = io.StringIO()
    iterator = iter(inputs)
    cli_app.run(inp=lambda prompt="": next(iterator), out=out)
    return out.getvalue()


def test_menu_quit(monkeypatch, tmp_path: Path) -> None:
    output = _run_with_inputs(["5"], monkeypatch, tmp_path)
    assert "main menu" in output
    assert "Goodbye." in output


def test_about_screen(monkeypatch, tmp_path: Path) -> None:
    output = _run_with_inputs(["4", "5"], monkeypatch, tmp_path)
    assert "AstraNotes" in output
    assert "CSEN 296B-2" in output


def test_settings_lists_data_dir(monkeypatch, tmp_path: Path) -> None:
    output = _run_with_inputs(["3", "5"], monkeypatch, tmp_path)
    assert "Data directory" in output
    assert str(tmp_path) in output
    assert "ASTRANOTES_KEY" in output


def test_create_then_list_round_trip(monkeypatch, tmp_path: Path) -> None:
    inputs = [
        "1", "shopping", "milk", "n",
        "2",
        "5",
    ]
    output = _run_with_inputs(inputs, monkeypatch, tmp_path)
    assert "Saved note" in output
    assert "shopping" in output
    assert "milk" in output


def test_create_rejects_empty_title(monkeypatch, tmp_path: Path) -> None:
    inputs = ["1", "   ", "body", "n", "5"]
    output = _run_with_inputs(inputs, monkeypatch, tmp_path)
    assert "Could not save note" in output
