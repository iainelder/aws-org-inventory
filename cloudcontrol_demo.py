# type: ignore

import json
import sys

import boto3
import pandas


def main():

    type_name = sys.argv[1]
    print(dump_resources(type_name))


def dump_resources(type_name):

    resources = list_resources(type_name)
    return pandas.DataFrame(resources).to_csv(index=False)


def list_resources(type_name):

    resp = boto3.client("cloudcontrol").list_resources(TypeName=type_name)
    return [flatten_resource(r, resp) for r in resp["ResourceDescriptions"]]


def flatten_resource(resource, response):
    return {
        **{"Identifier": resource["Identifier"], "TypeName": response["TypeName"]},
        **json.loads(resource["Properties"]),
    }


if __name__ == "__main__":
    main()
