from typing import List

import tomli
from pydantic import BaseModel, conlist

# Need to use Annotated because of pydantic's incompatibility with mypy.
# See https://github.com/samuelcolvin/pydantic/issues/156
from typing_extensions import Annotated


class OrgConfigError(Exception):
    pass


class OrgInput(BaseModel):
    org_name: str
    management_profile: str
    regions: Annotated[List[str], conlist(str, min_items=1)]


class OrgListInput(BaseModel):
    orgs: Annotated[List[OrgInput], conlist(OrgInput, min_items=1)]


def load() -> OrgListInput:
    with open("orgs.toml", mode="rb") as f:
        config_dict = tomli.load(f)
        return OrgListInput(**config_dict)


# @dataclass
# class OrgConfig:
#     def __init__(self, config: OrgListInput) -> None:

#         if not isinstance(config, dict):
#             raise OrgConfigError("config is not a dict")

#         try:
#             orglist = config["orgs"]
#         except KeyError:
#             raise OrgConfigError("config has no `orgs` key")

#         if not isinstance(orglist, list):
#             raise OrgConfigError("`orgs` key is not a list of orgs")

#         for index, org in enumerate(orglist):
#             if not isinstance(org, dict):
#                 raise OrgConfigError(f"`orgs` item at index {index} is not a dict")
