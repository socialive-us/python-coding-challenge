"""
Title: app.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import os
import re
import json
import logging
from uuid import uuid4
from typing import Dict, Optional
from datetime import datetime

import boto3
import requests
from botocore.exceptions import ClientError
from pydantic import BaseModel, ValidationError, validator

# Constants

API_PATH = "/api/v1/accounts"  # Path to this capability's API
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")  # DynamoDB table name
MAX_LENGTH_STRING = 255
PATTERN = r'^[a-z0-9.-]+\.[a-z]{2,63}$'

# Globals
aws_region = "us-east-1"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb_client = boto3.client("dynamodb", region_name=aws_region)


class ConditionExpressionException(Exception):
    def __init__(self, message, status_code, additional_info=None):
        super().__init__(message)
        self.status_code = status_code
        self.additional_info = additional_info or {}

class RequestBodyException(Exception):
    def __init__(self, message, status_code, additional_info=None):
        super().__init__(message)
        self.status_code = status_code
        self.additional_info = additional_info or {}


def basic_check_for_strings(field_label, value):
    if value is None:
        raise ValueError(f"{field_label} may not be null")
    if value.isspace():
        raise ValueError(f"{field_label} may not be empty")
    if len(value) > MAX_LENGTH_STRING:
        raise ValueError(f"{field_label} may not be more than 255 characters")

# Request Body

class CreateTenantRequest(BaseModel):
    """
    Request body for the POST endpoint
    """
    name: Optional[str] = ...  # A required field that can be None
    website: Optional[str] = ...  # A required field that can be None
    comment: Optional[str]

    @validator("name", allow_reuse=True)
    def _is_valid_name(cls, value):
        basic_check_for_strings('name', value)
        return value

    @validator("website", allow_reuse=True)
    def _is_valid_website(cls, value):
        basic_check_for_strings('website', value)
        if not re.match(PATTERN, value):
            raise ValueError("Invalid website domain")

        return value


def lambda_handler(event, _context):
    """
    Main handler method for the Create Tenant Lambda

    :param event: Event data passed into the Lambda
    :param _context: Runtime information for the Lambda, unused
    (https://docs.aws.amazon.com/lambda/latest/dg/python-context.html)
    """
    try:
        logger.info(json.dumps(event, default=str))
        request_body = _verify_request_body(event["body-json"])

        account_id = str(uuid4())
        item_response = _create_item(
            dynamodb_client,
            DYNAMODB_TABLE_NAME,
            account_id,
            request_body
        )

        return _build_response(True, item_response, f"{API_PATH}/{account_id}")
    
    except (RequestBodyException, ConditionExpressionException) as e:
        return _build_response(False, {'statusCode': e.status_code, 'message': e.message})

    except Exception as ex:
        logger.error("%s: %s", type(ex), ex, exc_info=True)
        raise ex


def _build_response(success_response: bool, response: Dict, api_path: str = None) -> Dict:
    """
    Create the response object that will be serialized
    """
    if success_response:
        response['header'] = {'Location': api_path}
        response['statusCode'] = requests.codes.created

    logger.info(response)
    return response


def _verify_request_body(body: Dict[str, str]) -> CreateTenantRequest:
    try:
        request_body = CreateTenantRequest(**body)
        return request_body

    except ValidationError as ex:
        err_msg = ""
        for err in ex.errors():
            if err_msg:
                err_msg += "; "
            if err["msg"] == "field required":
                fields = ""
                for field in err["loc"]:
                    if fields:
                        fields += ", "
                    fields += field
                err_msg += f"{fields} may not be missing"
            else:
                err_msg += f"{err['msg']}"
        logger.error(err_msg)
        raise RequestBodyException(err_msg, status_code=requests.codes.bad_request)


def _create_item(
    dynamodb_client: boto3.client,
    table_name: str,
    account_id: str,
    request_body: CreateTenantRequest,
) -> Dict:
    try:
        item = {
            'accountId': {'S': account_id},
            'name': {'S': request_body.name},
            'website': {'S': request_body.website},
            'created_at': {'S': datetime.now().isoformat()},
            'updated_at': {'S': datetime.now().isoformat()},
        }
        if request_body.comment:
            item['comment'] = {'S': request_body.comment}

        dynamodb_client.put_item(
            TableName=table_name,
            Item=item,
            ConditionExpression='attribute_not_exists(accountId)',
        )
        item_dict = request_body.dict()
        item_dict['id'] = account_id
        return {'item': item_dict}

    except ClientError as ex:
        logger.error("%s: %s", type(ex), ex, exc_info=True)
        raise ConditionExpressionException('Conflict with item', status_code=requests.codes.conflict)
