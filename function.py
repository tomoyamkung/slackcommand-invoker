import json
import logging
import os
import urllib.parse
from typing import List

import boto3

def lambda_handler(event: dict, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(json.dumps(event))

    if "challenge" in event:
        return event.get("challenge")

    logger.info(json.dumps(event.get("body")))

    text_params: List["str"] = [
        element for element in event.get("body").split("&") if element.startswith("text=")
    ]
    params: List["str"] = urllib.parse.unquote_plus(text_params[0].removeprefix("text=")).split(" ")
    logger.info({"params": params})

    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=os.environ["LAMBDA_FUNCTION_NAME"],
        InvocationType="Event",
        LogType="Tail",
        Payload=json.dumps({"params": params})
    )

    return {
        "statusCode": 200,
        "body": json.dumps("OK")
    }
