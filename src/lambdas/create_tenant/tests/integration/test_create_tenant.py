"""
Title: test_create_tenant.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
# the first import is moto, so that moto gets loaded BEFORE the app.py and boto* modules
from moto import mock_dynamodb, mock_stepfunctions
import json
import os
import boto3
import pytest

ACCOUNT_NAME = "test-account"
WEBSITE = "www.example.com"


def generate_api_gateway_event():
    return {
        "body-json": {
            "name": ACCOUNT_NAME,
            "website": WEBSITE,
        },
        "params": {
            "querystring": {},
            "header": {
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Host": "ndh8gj2sm7.execute-api.us-east-1.amazonaws.com",
                "User-Agent": "test-user-agent",
                "X-Amzn-Trace-Id": "Root=1-61974ca4-5af6d6c16acbfd181ba928d2",
                "X-Forwarded-For": "test-invoke-source-ip",
                "X-Forwarded-Port": "443",
                "X-Forwarded-Proto": "https"
            }
        },
        "stage-variables": {
            "deploymentId": "95777ed2-5582-44ee-b3d3-269dc74e865b"
        },
        "context": {
            "account-id": "467500726336",
            "api-id": "g2xa6vbk37",
            "api-key": "test-invoke-api-key",
            "authorizer-principal-id": "",
            "caller": "AROAIW2WQDF2CXMCCSPZI:foo@example.com",
            "cognito-authentication-provider": "",
            "cognito-authentication-type": "",
            "cognito-identity-id": "",
            "cognito-identity-pool-id": "",
            "http-method": "POST",
            "request-id": "1234",
            "stage": "test-invoke-stage",
            "source-ip": "test-invoke-source-ip",
            "user": "AROAIW2WQDF2CXMCCSPZI:foo@example.com",
            "user-agent": "test-user-agent"
        }
    }


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
def app(env_variables):
    from create_tenant.handler import app

    yield app


def test_tenant_created(app):
    """
    Verify the success case
    """
    # Invoke handler
    response = app.lambda_handler(generate_api_gateway_event(), None)

    assert response["statusCode"] == 201
    assert f"/accounts/" in response["header"]["Location"]
    #assert response["body"]["name"] == ACCOUNT_NAME
    #assert response["body"]["website"] == WEBSITE