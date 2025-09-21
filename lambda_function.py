import json
import boto3
import base64

s3 = boto3.client('s3')
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
BUCKET_NAME = 'smechatbots3'

# --- Helpers ---
def extract_text(file_content, file_name):
    # For POC, don’t parse PDF, just return dummy or decoded text
    try:
        return file_content.decode("utf-8", errors="ignore")
    except Exception:
        return "Sample extracted text for testing"

def split_text_into_chunks(text, chunk_size=200):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def embed_text(chunk):
    body = json.dumps({"inputText": chunk})
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=body
    )
    return json.loads(response["body"].read())["embedding"]

def store_vector(doc_id, chunks, embeddings):
    """Store vectors (pseudo-code). Replace with OpenSearch/DB insert."""
    print(f"Storing {len(embeddings)} embeddings for {doc_id}")
    # Example: put into DynamoDB / OpenSearch
    # db_client.put_item(...)


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
        # 1. Upload the file to S3 
        upload_status = upload_file_to_s3(file_content, file_name)
        print(upload_status)
        # 2. Extract the text
        text = extract_text(file_content, file_name)

        # 3. Split text into chunks
        chunks = list(split_text_into_chunks(text))
        print(f"Created {len(chunks)} chunks from document")

        # 4. Generate embeddings
        embeddings = [embed_text(chunk) for chunk in chunks]
        print(f"Generated {len(embeddings)} embeddings")

        # 5. Store vectors (stub for now)
        store_vector(file_name, chunks, embeddings)

        return create_response(200, {"message": f"File processed and embedded with {len(embeddings)} chunks."})
    
    except Exception as e:
        return create_response(500, {"error": str(e)})

