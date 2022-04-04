from contextlib import contextmanager
from typing import Any, ContextManager, Iterator

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from org_config import OrgConfig, load_org_config


@contextmanager
def does_not_raise() -> Iterator[None]:
    yield


def test_load_config_reads_toml(mocker: MockerFixture) -> None:

    mocker.patch(
        "org_config.open",
        mocker.mock_open(
            read_data=(
                b'organization_name = "org1"\n'
                b'management_profile = "profile1"\n'
                b'regions = ["eu-west-1"]\n'
            )
        ),
    )

    load_org_config()

    import org_config

    org_config.open.assert_called_once_with("org_config.toml", mode=mocker.ANY)  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "parsed_input, expected_exception",
    [
        pytest.param(None, pytest.raises(TypeError), id="None"),
        pytest.param({}, pytest.raises(ValidationError), id="empty dict"),
        pytest.param(
            {
                "organization_name": "",
                "management_profile": "profile1",
                "regions": ["eu-west-1"],
            },
            pytest.raises(ValidationError),
            id="empty organization_name",
        ),
        pytest.param(
            {
                "organization_name": "org1",
                "management_profile": "",
                "regions": ["eu-west-1"],
            },
            pytest.raises(ValidationError),
            id="empty management_profile",
        ),
        pytest.param(
            {
                "organization_name": "org1",
                "management_profile": "profile1",
                "regions": [],
            },
            pytest.raises(ValidationError),
            id="empty regions",
        ),
        pytest.param(
            {
                "organization_name": "org1",
                "management_profile": "profile1",
                "regions": ["eu-west-1", "eu-toybox-1"],
            },
            pytest.raises(ValidationError),
            id="invalid region",
        ),
    ],
)
def test_invalid_input(
    parsed_input: Any, expected_exception: ContextManager[Exception]
) -> None:
    with expected_exception:
        OrgConfig(**parsed_input)


@pytest.mark.parametrize(
    "loaded_config",
    [
        pytest.param(
            {
                "organization_name": "org1",
                "management_profile": "profile1",
                "regions": ["eu-west-1"],
            }
        )
    ],
)
def test_valid_config(loaded_config: Any) -> None:
    actual_config = OrgConfig(**loaded_config)
    assert actual_config.organization_name == "org1"
    assert actual_config.management_profile == "profile1"
    assert actual_config.regions == ["eu-west-1"]
