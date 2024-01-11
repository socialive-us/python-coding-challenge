"""
Title: test_create_tenant.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import pytest
from unittest.mock import patch

# Constants
ACCOUNT_NAME = "test-account"
WEBSITE = "www.example.com"
TEST_COMMENT = "test-comment"
CREATED = 201
BAD_REQUEST = 400
CONFLICT = 409


def generate_api_gateway_event():
    return {
        "body-json": {
            "name": ACCOUNT_NAME,
            "website": WEBSITE,
            "comment": TEST_COMMENT,
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


def test_tenant_created(app):
    """
    Verify the success case
    """
    response = app.lambda_handler(generate_api_gateway_event(), None)
    response = app.lambda_handler(generate_api_gateway_event(), None)

    item = response.get('item')
    item_id = item.get('id')

    assert response["statusCode"] == CREATED
    assert f"/accounts/{item_id}" in response["header"]["Location"]
    assert response.get("item").get("name") == ACCOUNT_NAME
    assert response.get("item").get("website") == WEBSITE


def test_tenant_conflict_409(app):
    mock_response = (False, {'statusCode': CONFLICT, 'message': 'Conflict with item'})
    with patch('create_tenant.handler.app._create_item', return_value=mock_response) as m:
        response = app.lambda_handler(generate_api_gateway_event(), None)

        m.assert_called_once()
        assert response.get("statusCode") == CONFLICT
        assert response.get('message') == 'Conflict with item'


def test_tenant_error_400(app):
    event = generate_api_gateway_event()
    event['body-json']['website'] = None

    response = app.lambda_handler(event, None)
    assert response.get("statusCode") == BAD_REQUEST
    assert response.get('message') == 'website may not be null'


def test_lambda_exits_with_error(app):
    with patch('create_tenant.handler.app._create_item', side_effect=Exception):
        with pytest.raises(Exception):
            app.lambda_handler(generate_api_gateway_event(), None)
