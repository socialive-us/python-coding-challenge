"""
Title: test_verify_request_body.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import pytest

ACCOUNT_NAME = "test-account"
WEBSITE = "www.example.com"
BAD_REQUEST = 400

valid_body = {
    "name": ACCOUNT_NAME,
    "website": WEBSITE
}

fields = ["name", "website"]


def test_verify_request_body():
    """
    Verify success case
    """
    from create_tenant.handler.app import _verify_request_body

    success, request_body = _verify_request_body(valid_body)

    assert success
    assert request_body.name == ACCOUNT_NAME
    assert request_body.website == WEBSITE


def test_verify_request_body_with_missing_fields():
    """
    Verify validation of missing fields
    """
    from create_tenant.handler.app import _verify_request_body

    for field in fields:
        copy = valid_body.copy()
        del copy[field]
        expected_response = {"statusCode": BAD_REQUEST,  'message': f'{field} may not be missing'}
        success, response = _verify_request_body(copy)
        assert not success
        assert response == expected_response

    expected_response = {"statusCode": BAD_REQUEST, "message": "name may not be missing; website may not be missing"}
    success, response = _verify_request_body({ })
    assert not success
    assert response == expected_response


def test_verify_request_body_with_null_fields():
    from create_tenant.handler.app import _verify_request_body

    for field in fields:
        copy = valid_body.copy()
        copy[field] = None
        expected_response = {"statusCode": BAD_REQUEST, "message": f"{field} may not be null"}
        success, response = _verify_request_body(copy)
        assert not success
        assert response == expected_response


def test_verify_request_body_with_only_whitespace_fields():
    from create_tenant.handler.app import _verify_request_body

    for field in fields:
        copy = valid_body.copy()
        copy[field] = ' '
        expected_response = {"statusCode": BAD_REQUEST, "message": f"{field} may not be empty"}
        success, response = _verify_request_body(copy)
        assert not success
        assert response == expected_response


def test_verify_request_body_with_invalid_name():
    """
    Verify validation of invalid fields
    """
    from create_tenant.handler.app import _verify_request_body

    test_data = {
        "x" * 256: "name may not be more than 255 characters"
    }
    for account_name, err_msg in test_data.items():
        copy = valid_body.copy()
        copy["name"] = account_name
        expected_response = {"statusCode": BAD_REQUEST, "message": err_msg}
        success, response = _verify_request_body(copy)
        assert not success
        assert response == expected_response


def test_verify_request_body_with_invalid_domain_website():
    """
    Verify validation of invalid fields
    """
    from create_tenant.handler.app import _verify_request_body

    copy = valid_body.copy()
    copy['website'] = 'Invalid domain'
    success, response = _verify_request_body(copy)
    assert not success
    assert response == {'message': 'Invalid website domain', 'statusCode': BAD_REQUEST}

    copy['website'] = 'www.novaliddomain.c'
    success, response = _verify_request_body(copy)
    assert not success
    assert response == {'message': 'Invalid website domain', 'statusCode': BAD_REQUEST}
