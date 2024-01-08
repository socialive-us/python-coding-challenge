"""
Title: test_verify_request_body.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import pytest


ACCOUNT_NAME = "test-account"
WEBSITE = "www.example.com"

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

    request_body = _verify_request_body(valid_body)

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
        expected_err_msg = '{"statusCode": 400, "message": "' + field + ' may not be missing"}'
        with pytest.raises(Exception, match=expected_err_msg):
            _verify_request_body(copy)

    expected_err_msg = '{"statusCode": 400, "message": "name may not be missing; website may not be missing"}'
    with pytest.raises(Exception, match=expected_err_msg):
        _verify_request_body({ })


# TODO write test for null (None) fields


# TODO write test for fields that only have whitespace


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
        expected_err_msg = '{"statusCode": 400, "message": "' + err_msg + '"}'
        with pytest.raises(Exception, match=expected_err_msg):
            _verify_request_body(copy)


# TODO write test for validating the website URL