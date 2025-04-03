import os
import boto3
import json
import ast

# AWS S3 setup
S3_BUCKET = os.environ.get("S3_BUCKET", "your-s3-bucket-name")
s3_client = boto3.client("s3")

def download_from_s3(s3_key):
    """Downloads a file from S3 and returns its content."""
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
    return obj['Body'].read().decode('utf-8')

def parse_python_code(code):
    """Parses the Python code into an AST and extracts relevant information."""
    tree = ast.parse(code)
    
    parsed_data = {
        "functions": [],
        "classes": [],
        "variables": [],
        "imports": [],
        "comments": []
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            parsed_data["functions"].append({
                "name": node.name,
                "arguments": [arg.arg for arg in node.args.args],
                "return_type": "unknown",
                "docstring": ast.get_docstring(node)
            })
        elif isinstance(node, ast.ClassDef):
            class_data = {
                "name": node.name,
                "methods": [],
                "docstring": ast.get_docstring(node)
            }
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    class_data["methods"].append({
                        "name": class_node.name,
                        "arguments": [arg.arg for arg in class_node.args.args],
                        "docstring": ast.get_docstring(class_node)
                    })
            parsed_data["classes"].append(class_data)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    parsed_data["variables"].append({
                        "name": target.id,
                        "type": "unknown",
                        "initialization": ast.dump(node.value)
                    })
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            for alias in node.names:
                parsed_data["imports"].append(f"import {alias.name}")
    
    return parsed_data

def lambda_handler(event, context):
    """AWS Lambda entry point to process S3 files."""
    try:
        # Get the S3 key (path to the file) from the event
        s3_key = event['s3_key']
        
        # Download the file from S3
        file_content = download_from_s3(s3_key)
        
        # Parse the Python code
        parsed_code = parse_python_code(file_content)
        
        # Return parsed code as JSON
        return {
            'statusCode': 200,
            'body': json.dumps(parsed_code)
        }
    
    except Exception as e:
        print(f"ERROR: {str(e)}")  # Log error in CloudWatch
        return {
            "error": "Internal Server Error",
            "details": str(e)
        }
