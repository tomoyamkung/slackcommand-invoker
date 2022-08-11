import json
import logging
import os
import urllib.parse
from typing import List, Optional

import boto3


def lambda_handler(event: dict[str, str], context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(json.dumps(event))

    if "challenge" in event:
        return event.get("challenge")

    params: Optional[List[str]] = parse_params(event.get("body"))
    if params is not None:
        logger.info({"params": params})

    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=os.environ["LAMBDA_FUNCTION_NAME"],
        InvocationType="Event",
        LogType="Tail",
        Payload=json.dumps({"params": params}),
    )
    logger.info(response)

    return {"statusCode": 200, "body": json.dumps("OK")}


def parse_params(params_string: Optional[str]) -> Optional[List[str]]:
    if params_string is None:
        return None

    text_params: List["str"] = [
        element for element in params_string.split("&") if element.startswith("text=")
    ]
    if len(text_params) == 0:
        return None

    return urllib.parse.unquote_plus(text_params[0].removeprefix("text=")).split(" ")
