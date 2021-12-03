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

## Advanced example

Say you need to collect inventory about AWS Config itself. You want to know which config recorders exist and how the delivery streams are configured. You want to do this across multiple regions and multiple organizations.

aws-org-inventory doesn't yet support multiple API calls, multiple regions, or multiple organizations in a single invocation. So one way or another you'll need to perform multiple invocations.

[GNU Parallel](https://www.gnu.org/software/parallel/) offers a neat way to do this. First you export a bash function that takes a profile and a region as parameters and saves the results of all the invocations of aws-org-inventory. Then you invoke the function via parallel passing the a list of profiles and a list of regions. parallel iterates over the cartesian product of the parameters to collect all the data.

You can use a script like this to drive the whole process.

```bash
cd "$(mktemp --dir)"

collect() {
    profile="${1}"
    region="${2}"

    AWS_PROFILE="${profile}" \
    AWS_DEFAULT_REGION="${region}" \
    aws-org-inventory config describe_configuration_recorders ConfigurationRecorders \
    > "configuration_recorders__${profile}__${region}.csv"

    AWS_PROFILE="${profile}" \
    AWS_DEFAULT_REGION="${region}" \
    aws-org-inventory config describe_delivery_channels DeliveryChannels \
    > "delivery_channels__${profile}__${region}.csv"
}

export -f collect

time parallel --max-procs 1 collect \
::: org_A org_B \
::: us-east-1 eu-west-1
```

With some patience you will end up with a result like this.

```text
$ tree
.
├── configuration_recorders__org_A__eu-west-1.csv
├── configuration_recorders__org_A__us-east-1.csv
├── configuration_recorders__org_B__eu-west-1.csv
├── configuration_recorders__org_B__us-east-1.csv
├── delivery_channels__org_A__eu-west-1.csv
├── delivery_channels__org_A__us-east-1.csv
├── delivery_channels__org_B__eu-west-1.csv
├── delivery_channels__org_B__us-east-1.csv
```

Patience is needed because this is a really inefficient way to collect from multiple APIs and multiple regions. This can definitely be improved in aws-org-inventory itself. I'll be working on that whenver I have the time and the notion.

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
