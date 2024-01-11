"""
Title: test_build_response.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import json
import pytest

API_PATH = "/test-api/v1/accounts"
CREATED = 201
BAD_REQUEST = 400
CONFLICT = 409


def test_build_response_success():
    """
    Verify success case
    """
    from create_tenant.handler.app import _build_response

    response = _build_response(
        True, {
            'item': {
                'id': 'test-account'
            }
        },
        f"{API_PATH}/test-account"
    )

    assert response.get('statusCode') == CREATED
    assert response.get('header').get('Location') == f"{API_PATH}/test-account"
    assert response.get('item') == {'id': 'test-account'}


def test_build_response_conflict_failure():
    """
    Verify failure case
    """
    from create_tenant.handler.app import _build_response

    response = _build_response(False, {
        'statusCode': CONFLICT,
        'message': 'test-error'
    })

    assert not response.get('header')
    assert response.get('statusCode') == CONFLICT
    assert response.get('message') == 'test-error'


def test_build_error():
    from create_tenant.handler.app import _build_error
    response = _build_error(BAD_REQUEST, 'test error message')

    assert response == {'statusCode': BAD_REQUEST, 'message': 'test error message'}
