from pathlib import Path

import pytest

from app.core.startup import validate_required_data_files


def test_required_data_files_are_present_and_valid() -> None:
    validate_required_data_files()


def test_startup_check_fails_when_required_data_is_missing() -> None:
    missing_root = Path(__file__).parent / "_missing_startup_data"

    with pytest.raises(RuntimeError, match="missing required data files"):
        validate_required_data_files(missing_root)
