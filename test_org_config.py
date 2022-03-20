from contextlib import contextmanager
from typing import Any, ContextManager, Dict, Iterator

import pytest  # type: ignore[import]
from pytest_mock import MockerFixture

import org_config
from org_config import OrgConfigError


@contextmanager
def does_not_raise() -> Iterator[None]:
    yield


def test_load_config_reads_toml(mocker: MockerFixture) -> None:

    mocker.patch(
        "org_config.open",
        mocker.mock_open(
            read_data=(
                b"[[orgs]]\n"
                b'org_name = "org1"\n'
                b'management_profile = "profile1"\n'
                b'regions = ["eu-west-1"]\n'
            )
        ),
    )

    org_config.load()

    org_config.open.assert_called_once_with("orgs.toml", mode=mocker.ANY)  # type: ignore[attr-defined]


# TODO: check errors using Pydantic ValidationError

# @pytest.mark.parametrize(  # type: ignore[misc]
#     "config,expectation",
#     [
#         pytest.param(
#             None, pytest.raises(OrgConfigError, match="config is not a dict"), id="None"
#         ),
#         pytest.param(
#             [],
#             pytest.raises(OrgConfigError, match="config is not a dict"),
#             id="empty list",
#         ),
#         pytest.param(
#             {},
#             pytest.raises(OrgConfigError, match="config has no `orgs` key"),
#             id="empty dict",
#         ),
#         pytest.param(
#             {"bread": "butter"},
#             pytest.raises(OrgConfigError, match="config has no `orgs` key"),
#             id="some other key",
#         ),
#         pytest.param(
#             {"orgs": "myorg"},
#             pytest.raises(OrgConfigError, match="`orgs` key is not a list of orgs"),
#             id="orgs is string",
#         ),
#         pytest.param(
#             {"orgs": ["myorg"]},
#             pytest.raises(OrgConfigError, match="`orgs` item at index 0 is not a dict"),
#             id="orgs list item is string",
#         ),
#         pytest.param(
#             {"orgs": [{}]},
#             pytest.raises(OrgConfigError, match="`orgs` item at index 0 is not a dict"),
#             id="orgs list item is string",
#         ),
#     ],
# )
# def test_empty_config(
#     config: OrgListInput, expectation: ContextManager[OrgConfigError]
# ) -> None:
#     with expectation:
#         OrgConfig(config)
