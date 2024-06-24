
# AWS CDK EKS project

This is a sample project for CDK development with Python to deploy EKS cluster.

## Prerequisites

- [Node.js](https://nodejs.org/) (v14.x or later)
- [AWS CLI](https://aws.amazon.com/cli/) (configured with your credentials)
- [Python 3.7+](https://www.python.org/downloads/)
- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) (v2.x)

## How to use - local development:
1. Create and activate a virtual environment:

```sh
$ python3 -m venv .venv
$ source .venv/bin/activate
```
2. Install the dependencies:

```sh
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
$ npm install -g aws-cdk
$ pre-commit install
$ pre-commit run --all-files
```
3. To run the tests for the custom construct:
```sh
$ pytest tests
```

## How to use - deploy cluster:

1. Before you start ensure that you've a VPC with atleast 2 subnets and the following environment variables are set:
```
$ export CDK_DEFAULT_ACCOUNT=<aws_account_id>
$ export CDK_DEFAULT_REGION=<aws_default_region>
```
2. At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```
3. Deploy cluster using the cdk deploy command. Grab a :coffee: and wait for cluster creation to finish and nginx controller to deploy.
```
$ cdk deploy --all
```
4. Once validated, don't forget to clean-up the stack.
```
$ cdk destroy --all
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
