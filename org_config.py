from typing import List

import boto3
import tomli
from pydantic import BaseModel, Field, validator


class OrgConfig(BaseModel):
    organization_name: str = Field(..., min_length=1)
    management_profile: str = Field(..., min_length=1)
    regions: List[str] = Field(..., min_items=1)

    @validator("regions", each_item=True)
    def region_is_available_in_boto3(cls: "OrgConfig", v: str) -> str:
        available_regions = boto3.Session().get_available_regions("ec2")
        assert v in available_regions, f"{v} is not an available region"
        return v


def load_org_config() -> OrgConfig:
    with open("org_config.toml", mode="rb") as f:
        config_dict = tomli.load(f)
        return OrgConfig(**config_dict)
