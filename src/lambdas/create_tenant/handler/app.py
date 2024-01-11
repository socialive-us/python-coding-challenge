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
PATTERN = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Globals
aws_region = "us-east-1"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb_client = boto3.client("dynamodb", region_name=aws_region)


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
        success, request_body = _verify_request_body(event["body-json"])
        if not success:
            return _build_response(success, request_body)
        
        account_id = str(uuid4())
        success, item_response = _create_item(
            dynamodb_client,
            DYNAMODB_TABLE_NAME,
            account_id,
            request_body
        )

        return _build_response(success, item_response, f"{API_PATH}/{account_id}")

    except Exception as ex:
        logger.error("%s: %s", type(ex), ex, exc_info=True)
        raise ex


def _build_response(success: bool, response: Dict, api_path: str = None) -> Dict:
    """
    Create the response object that will be serialized
    """
    if success:
        response['header'] = {'Location': api_path}
        response['statusCode'] = requests.codes.created

    logger.info(response)
    return response


def _build_error(
        error_code: int = requests.codes.internal_server_error,
        message: str = "An internal server error occurred") -> str:
    """
    Create an error object that will be serialized.
    The statusCode field of this object is used to route
    to the appropriate API Gateway method response.
    """
    return {
        "statusCode": error_code,
        "message": message
    }


def _verify_request_body(body: Dict[str, str]) -> CreateTenantRequest:
    success = False
    try:
        request_body = CreateTenantRequest(**body)
        success = True
        return success, request_body
    
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
        return success, _build_error(requests.codes.bad_request, err_msg)


def _create_item(
    dynamodb_client: boto3.client,
    table_name: str,
    account_id: str,
    request_body: CreateTenantRequest,
) -> Dict:
    success = False
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
        success = True
        return success, {'item': item_dict}

    except ClientError as ex:
        logger.error("%s: %s", type(ex), ex, exc_info=True)
        return success, _build_error(requests.codes.conflict, 'Conflict with item')
