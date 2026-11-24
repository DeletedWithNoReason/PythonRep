import io
from contextlib import redirect_stdout
from pathlib import Path
import pytest

import blocknot
import inventory_system


BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "barakhlo.csv"
GOLDEN_PATH = BASE_DIR / "golden_master.txt"


def test_legacy_zvit_matches_golden_master(monkeypatch):
    monkeypatch.setattr(blocknot, "rich", [])
    expected = GOLDEN_PATH.read_text(encoding="utf-8")

    buf = io.StringIO()
    with redirect_stdout(buf):
        blocknot.zvit(str(CSV_PATH))

    assert buf.getvalue() == expected


def test_new_system_legacy_report_matches_golden_master():
    expected = GOLDEN_PATH.read_text(encoding="utf-8")
    inv = inventory_system.load_legacy_csv(str(CSV_PATH))
    actual = inventory_system.render_legacy_report(inv)
    assert actual == expected