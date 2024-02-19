from battle_analyzer.error import AnalyzerError
import json
from battle_analyzer.utils import replace_decimals

def make_response(result: dict) -> dict:
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(replace_decimals(result))
    }

def make_error_response(error: AnalyzerError) -> dict:
    code = error.code.value
    data = { 'error': { 'msg': error.msg, 'code': code } }
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(replace_decimals(data))
    }