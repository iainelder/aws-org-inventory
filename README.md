# AWS Org Inventory

Dumps to CSV all the resources in an organization's member accounts.

Set your environment's AWS_PROFILE and AWS_DEFAULT_REGION variables.

The AWS_PROFILE should be configured to use a role in the organization management account that can assume OrganizationAccountAccessRole in the member accounts.

Redirect the dumper's output to save the file.

The dumper uses Botocove to query each member account.

## Why?

This tool fills in the gaps in AWS Config's inventory.

Sadly [AWS Config](https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html) supports only a subset of all the resource types you may have.

AWS Config's organization aggregators are great, but they may not update instantly with new resources.

## Installation

The package is published to PyPy as aws-org-inventory, so you can install it with pip or anything equivalent.

```
pip install aws-org-inventory
```

## Basic example

Configure environment:

```bash
export AWS_PROFILE=OrgMgmtRole
export AWS_DEFAULT_REGION=eu-west-1
```

Dump inventory of CloudWatch log groups:

```bash
aws-org-inventory logs describe_log_groups logGroups
```

Dump inventory of support cases:

```bash
aws-org-inventory support describe_cases cases
```

Dump inventory of EC2 key pairs:

```bash
aws-org-inventory ec2 describe_key_pairs KeyPairs
```

Dump inventory of account alises:

```bash
aws-org-inventory iam list_account_alises AccountAliases
```

Try doing those with AWS Config!

## General use

To derive arguments for other use cases, check the boto service documentation.

The value passed to the boto3.client method that would instantiate a client for the service is parameter 1.

Find the method of that client that `list`s or `describe`s the resource type that you want to dump.

The name of the method is parameter 2.

Find in the method's response syntax the top-level key for the list of objects.

The name of the key is parameter 3.

## Error output

On stderr you will always see a summary of the botocove result and any exceptions. These exceptions may reveal problems such as an incorrect command invocation, a misconfigured AWS account, or a bug in the program (feel free to report those!)

If Botocove fails to get a session for an account, it will output the ID to stderr like this.

```text
Invalid session Account IDs as list: ['111111111111']
```

That account's resources will not be included in the main output.

## Development

Use Poetry to build and push a new version to PyPI.

```bash
poetry build
poetry publish
```

## TODO

TODO: query multiple regions (see aws-boto-multiregion-client for example)

TODO: export to JSON by default to simplify the output format (tabularization is tricky)

TODO: ensure that org management account is included in results

TODO: give example of how to use AwsOrgInventory class in other applications

TODO: improve CLI (monkey patch awscli.clidriver.CLIOperationCaller._make_client_call)

TODO: Use boto's service model to automate the parameters given a resource type

TODO: improve error handling
