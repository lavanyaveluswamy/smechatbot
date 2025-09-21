import json
import boto3
import base64

s3 = boto3.client('s3')
BUCKET_NAME = 'smechatbots3'

def create_response(status_code, message):
    return {
        'statusCode': status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps({"message": message})
    }

#Create a method to upload a file to S3
def upload_file_to_s3(file_content, file_name):
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content)
        return create_response(200, "File uploaded successfully!")
    except Exception as e:
        return create_response(500, f"Error: {str(e)}")

def lambda_handler(event, context):
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        if 'file' not in body or 'filename' not in body:
            return create_response(400, {"error": "Missing 'file' or 'filename' in request body"})
        file_content = base64.b64decode(body['file'])
        file_name = body['filename']
        return upload_file_to_s3(file_content, file_name)
    except Exception as e:
        return create_response(500, {"error": str(e)})

