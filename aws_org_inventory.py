from dataclasses import dataclass
import typing
from pprint import pprint
import json
import operator
import sys
import traceback

import pandas as pd
import botocove
import boto3

from boto_collator_client import CollatorClient

__version__ = '0.2.0'

def main():

    _, service, api, resource_type = sys.argv

    dump_inventory_to_csv(service, api, resource_type)
 

def dump_inventory_to_csv(service, api, resource_type):

    inv = AWSOrgInventory(
        service=service,
        api=api,
        resource_type=resource_type
    )

    try:
        print(
            inv
            .collect()
            .results_to_data_frame()
            .to_csv()
        )
    except Exception as ex:
        print(traceback.format_exc(), file=sys.stderr)
        print("Something went wrong. Here's the botocove response for debugging.", file=sys.stderr)
        print(inv.response, file=sys.stderr)
    finally:
        print(inv.summarize_collection(), file=sys.stderr)
        if inv.response["Exceptions"]:
            print(inv.response["Exceptions"], file=sys.stderr)


@dataclass
class AWSOrgInventory(object):

    service: str
    api: str
    resource_type: str
    role_name: str = "OrganizationAccountAccessRole"
    role_session_name: str = "AWSOrgInventory"
    response: typing.Any = None


    def collect(self):

        @botocove.cove(rolename=self.role_name, role_session_name=self.role_session_name)
        def _collect_from_org(session, service, api):
            cc = CollatorClient(session.client(service))
            return getattr(cc, api)()


        self.response = _collect_from_org(self.service, self.api)
        return self
    

    def results_to_data_frame(self):

        return (
            pd.DataFrame(self.response["Results"])
            .assign(ResourceList=lambda df: df.Result.apply(
                operator.itemgetter(self.resource_type)))
            .loc[lambda df: df["ResourceList"].apply(len) > 0]
            .explode("ResourceList")
            .apply(lambda row: {**row.to_dict(), **row.ResourceList}, axis=1,
                result_type="expand")
            .drop(["Result","ResourceList"], axis=1)
        )

    def summarize_collection(self):

        return {k: sum(1 for e in v) for k, v in self.response.items()}

if __name__ == "__main__":
    main()
