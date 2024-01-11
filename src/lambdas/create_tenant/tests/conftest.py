from moto import mock_dynamodb
import os

import pytest
import boto3


TABLE_NAME = "testing-table"


@pytest.fixture(scope="module")
def env_variables():
    """
    Mock AWS Credentials for moto
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def dynamodb_client(env_variables) -> boto3.client:
    """
    Mock DynamoDB client
    """
    with mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName=TABLE_NAME,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                { "AttributeName": "accountId", "AttributeType": "S" },
            ],
            KeySchema=[
                { "AttributeName": "accountId", "KeyType": "HASH" }
            ]
        )

        yield client


@pytest.fixture(scope="function")
def app(env_variables, dynamodb_client):
    from create_tenant.handler import app

    app.DYNAMODB_TABLE_NAME = TABLE_NAME

    yield app