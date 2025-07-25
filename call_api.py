import requests
import json

# The URL of your Flask API endpoint
api_url = "http://127.0.0.1:8000/generate_job_description"

# The prompt for the job description
user_prompt = "We need a data scientist with expertise in machine learning, Python, and SQL, capable of building predictive models and analyzing large datasets."

# The JSON payload to send
payload = {
    "prompt": user_prompt
}

# Set the Content-Type header
headers = {
    "Content-Type": "application/json"
}

try:
    # Send the POST request
    response = requests.post(api_url, headers=headers, json=payload)

    # Raise an exception for HTTP errors (4xx or 5xx)
    response.raise_for_status()

    # Parse the JSON response
    response_data = response.json()

    print(response_data)
    
    # Print the generated job description
    if "job_description" in response_data:
        print("Generated Job Description:\n")
        print(response_data["job_description"])
    else:
        print("API did not return a 'job_description' key.")
        print("Full API Response:", json.dumps(response_data, indent=2))

except requests.exceptions.RequestException as e:
    print(f"Error calling the API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"API Response Content: {e.response.text}")
except json.JSONDecodeError:
    print("Failed to decode JSON from API response.")
    print(f"Raw API Response: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")