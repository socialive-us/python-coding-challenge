"""
Title: test_create_item.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import pytest
CONFLICT = 409


def test_create_item(dynamodb_client):
    """
    Verify success and failure case
    """
    from create_tenant.handler.app import _create_item, CreateTenantRequest, ConditionExpressionException
    item_json = {'name': 'test-name', 'website': 'www.testwebsite.com', 'comment': 'test-comment'}
    request_data = CreateTenantRequest(**item_json)

    response = _create_item(
        dynamodb_client, 
        'testing-table',
        '1',
        request_data
    )

    item_json['id'] = '1'
    assert response.get('item') == item_json

    with pytest.raises(ConditionExpressionException, match='Conflict with item'):
        response = _create_item(
            dynamodb_client, 
            'testing-table',
            '1',  # Repeated PK should raise error because of ConditionExpression (ConditionExpressionException)
            request_data
        )
