import json
import requests
import os

GITHUB_API_URL = "https://api.github.com/repos"

def get_repo_files(owner, repo, path="", token=None):
    """Fetches file contents from a GitHub repository"""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"{GITHUB_API_URL}/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {"error": f"Failed to fetch repository contents: {response.text}"}

    return response.json()

def get_file_content(file_url, token=None):
    """Fetches raw file content from GitHub"""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    response = requests.get(file_url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch file: {response.text}"}
    
    return response.text

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    try:
        # Example: Input JSON from event
        body = json.loads(event.get("body", "{}"))
        github_url = body.get("github_url")
        token = os.getenv("GITHUB_TOKEN")  # Use an environment variable for security
        
        if not github_url:
            return {"statusCode": 400, "body": json.dumps({"error": "GitHub URL is required"})}
        
        # Extract owner and repo from GitHub URL
        parts = github_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        
        # Fetch repository contents
        repo_files = get_repo_files(owner, repo, token=token)
        if "error" in repo_files:
            return {"statusCode": 500, "body": json.dumps(repo_files)}
        
        # Extract code from Python files
        extracted_code = {}
        for file in repo_files:
            if file["type"] == "file" and file["name"].endswith(".py"):  # Modify for other languages
                raw_content = get_file_content(file["download_url"], token=token)
                extracted_code[file["name"]] = raw_content
        
        return {
            "statusCode": 200,
            "body": json.dumps({"extracted_code": extracted_code})
        }
    
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
