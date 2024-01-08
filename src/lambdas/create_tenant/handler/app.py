"""
Title: app.py

Copyright (c) 2024 Socialive. All rights reserved.
See all trademarks at https://www.socialive.us/terms-of-service
"""
import json
import logging
import os
from typing import Dict, Optional
from botocore.exceptions import ClientError
import boto3
import requests
from pydantic import BaseModel, ValidationError, validator

# Constants

# Path to this capability's API
API_PATH = "/api/v1/accounts"

# DynamoDB table name
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")


# Globals
aws_region = "us-east-1"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb_client = boto3.client("dynamodb", region_name=aws_region)


# Request Body

class CreateTenantRequest(BaseModel):
    """
    Request body for the POST endpoint
    """
    name: Optional[str] = ...  # A required field that can be None
    website: Optional[str] = ...  # A required field that can be None

    @validator("name", allow_reuse=True)
    def _is_valid_name(cls, value):
        if value is None:
            raise ValueError("name may not be null")
        if value.isspace():
            raise ValueError("name may not be empty")
        if len(value) > 255:
            raise ValueError("name may not be more than 255 characters")

        return value

    @validator("name", allow_reuse=True)
    def _is_valid_website(cls, value):
        if value is None:
            raise ValueError("website may not be null")
        if value.isspace():
            raise ValueError("website may not be empty")
        if len(value) > 255:
            raise ValueError("website may not be more than 255 characters")

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

        account_id = 1

        # Persist the account in DynamoDB
        item = _create_item(
            dynamodb_client,
            DYNAMODB_TABLE_NAME,
            account_id)

        return _build_response(f"{API_PATH}/{account_id}")

    except Exception as ex:
        logger.error("%s: %s", type(ex), ex, exc_info=True)
        raise ex


def _build_response(api_path: str) -> Dict:
    """
    Create the response object that will be serialized
    """
    response = {
        "statusCode": requests.codes.created,
        "header": {
            "Location": api_path
        },
        "body": { }  # TODO return the body of the item that was created
    }
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
    return json.dumps(
        {
            "statusCode": error_code,
            "message": message
        }
    )


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
        raise Exception(_build_error(requests.codes.bad_request, err_msg))


def _create_item(
        dynamodb_client: boto3.client,
        table_name: str,
        account_id: str) -> Dict:  # TODO return object representing item in DB

    try:
        # TODO insert item in table, detecting conflicts without reading from the DB
        return None
    except ClientError as ex:
        logger.error("%s: %s", type(ex), ex, exc_info=True)
        # TODO detect a conflict and return a 409