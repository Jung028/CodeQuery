# Use Amazon Linux 2 base image for AWS Lambda with Python 3.9
FROM public.ecr.aws/lambda/python:3.9

# Set working directory
WORKDIR /app

# Copy requirements first (to leverage Docker caching)
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY backend/ .

# Set the Lambda handler (adjust to match function in main.py)
CMD ["main.lambda_handler"]
