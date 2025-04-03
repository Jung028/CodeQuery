FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
RUN pip install boto3

# Copy function code
COPY backend/lambda_function.py ${LAMBDA_TASK_ROOT}

# Set handler
CMD ["lambda_function.lambda_handler"]
