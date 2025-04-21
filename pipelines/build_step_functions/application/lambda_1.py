import boto3
import os
import json

def handler(event, context):
    sfn = boto3.client("stepfunctions")
    response = sfn.start_execution(
        stateMachineArn=os.environ.get("STEP_FUNCTION_ARN"),
        input=json.dumps(event)
    )
    return {
        "statusCode": 202,
        "body": json.dumps({"message": "Step Function iniciada", "executionArn": response["executionArn"]})
    }
