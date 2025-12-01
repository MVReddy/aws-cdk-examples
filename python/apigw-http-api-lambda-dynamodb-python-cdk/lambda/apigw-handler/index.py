# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch all supported libraries for X-Ray tracing
patch_all()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    request_id = context.request_id
    
    # Log request context for security and audit purposes
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Table name: {table}")
    
    # Extract source IP from request context
    source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
    logger.info(f"Source IP: {source_ip}")
    
    try:
        if event["body"]:
            item = json.loads(event["body"])
            item_id = item.get('id', 'unknown')
            logger.info(f"Processing item with id: {item_id}")
            
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])
            
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            
            logger.info(f"Successfully inserted item with id: {item_id}")
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
        else:
            logger.info("Received request without a payload, inserting default data")
            default_id = str(uuid.uuid4())
            
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": default_id},
                },
            )
            
            logger.info(f"Successfully inserted default item with id: {default_id}")
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal server error"}),
        }
