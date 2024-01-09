### python-coding-challenge

This project is used for interviews.

### Dependencies

* Python3
* pip3
* virtualenv

#### Linux (Ubuntu)

```
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

#### MacOS

```
brew update
# First time python installation
brew install python
# Or, if python is already installed, but not Python3
brew upgrade python
```

### Activate the Virtual Environment

First time:
```
mkdir .venv
python3 -m venv .venv
source .venv/bin/activate
```

Each following time:
```
source .venv/bin/activate
```

### Run Automated Tests

Activate the virtual environment, then

```
cd src/lambdas
./run_tests.sh
```

The script fails because the code coverage is below 90%.

### Coding Challenge

This is an AWS serverless application with a DynamoDB table. The create_tenant Lambda is invoked by a POST with a request body, to persist a Tenant to a table. For this application, the Tenant is an "account".

No AWS resources are required to run the Lambda locally, as the DynamoDB table can be mocked with the [moto](https://github.com/getmoto/moto) framework and verified with the `run_tests.sh` script.

Fork the repository, create a branch, and update the code to:

- Update the POST body:
  - Validate the `website` field to be a valid domain name
  - Add at least one more field to the account
- Persist the item in the DynamoDB table
  - Allocate a unique identifier and return it in the response
  - Create the item in the table, detecting collisions without first reading the item (hint: ConditionalExpression)
  - Add a createdAt and updatedAt field to the table, but do not return it in the response
- Evolve the tests to have 90% or greater coverage
  - Update integration and unit tests, deciding what should be unit vs. integration

Once done, create a pull request. The changes will be reviewed together. No AWS resources are required because the Lambda will be demonstrated with `run_tests.sh`, using mocked resources.
