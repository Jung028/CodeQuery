from lambda_function import lambda_handler

# Simulate event data
event = {
    'code': """def hello_world():
    print('Hello, World!')
    
    def add(a, b):
        return a + b"""
}

# Simulate a dummy context (you can pass `None` if not used)
context = None

# Call the lambda handler function with the simulated event and context
response = lambda_handler(event, context)

# Print the response to see the result
print(response)
