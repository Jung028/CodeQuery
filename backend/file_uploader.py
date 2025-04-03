import os
import boto3

# AWS S3 setup
S3_BUCKET = "your-s3-bucket-name"
s3_client = boto3.client("s3")

def upload_to_s3(file_content, s3_key):
    """Uploads a file to S3 and returns the S3 URL."""
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_content)
    return f"s3://{S3_BUCKET}/{s3_key}"

def upload_repo_files_to_s3(repo_path):
    """Uploads files from the cloned repo to S3."""
    uploaded_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_content = f.read()
            s3_key = f"repos/{file}"
            upload_url = upload_to_s3(file_content, s3_key)
            uploaded_files.append(upload_url)
    return uploaded_files

repo_path = "/path/to/cloned/repo"  # Path to the cloned repository
uploaded_files = upload_repo_files_to_s3(repo_path)
print(f"Files uploaded: {uploaded_files}")
