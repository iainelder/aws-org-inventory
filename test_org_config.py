import pytest  # type: ignore[import]

from org_config import InvalidConfigError, OrgConfig


def test_empty_config() -> None:
    with pytest.raises(InvalidConfigError):
        OrgConfig({})
