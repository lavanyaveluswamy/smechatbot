import json
import boto3
import base64

s3 = boto3.client('s3')
BUCKET_NAME = 'smechatbots3'

def lambda_handler(event, context):
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        if 'file' not in body or 'filename' not in body:
            return {
                'statusCode': 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'body': json.dumps({"error": "Missing 'file' or 'filename' in request body"})
            }
        file_content = base64.b64decode(body['file'])
        file_name = body['filename']
        s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content)
        return {
            'statusCode': 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            'body': json.dumps({"message": "File uploaded successfully!"})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            'body': json.dumps({"error": str(e)})
        }
