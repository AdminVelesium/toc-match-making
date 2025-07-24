import requests
import json

url = "http://127.0.0.1:8000/match"

payload = {
  "candidate_details": {
    "candidate_id": "37ybhbye888e",
    "years_of_exp": 5,
    "skills": ["Python", "Java", "UI/UX"],
    "Tools": ["MS Dynamic GP", "MongoDB", "SnowFlake"],
    "Work Experience": "Developed and deployed scalable Python microservices on AWS. Designed and managed MongoDB databases. Implemented UI/UX improvements for web applications.",
    "self_intro": "Highly motivated software engineer with a passion for building robust and efficient systems. Eager to contribute to innovative projects."
  },
  "job_description": {
    "_id": { "$oid": "687e2806629e2b477e755076" },
    "jobTitle": "Senior Backend Engineer",
    "location": "Bangalore, Karnataka, India",
    "employmentType": "full-time",
    "jobCategory": "software-development",
    "salaryRange": { "min": 130000, "max": 150000 },
    "experienceLevel": "senior",
    "companyName": "VELESIUM LABS",
    "jobDescription": "Develop and maintain scalable backend services using Python. Design and implement RESTful APIs. Collaborate with cross-functional teams.",
    "responsibilities": "Lead development efforts, mentor junior engineers, ensure code quality and performance.",
    "applicationEmail": "ABC@VELESIUM.COM",
    "screeningQuestions": ["Describe your experience with large-scale systems."],
    "keySkills": ["PYTHON", "AWS", "Docker", "Kubernetes", "Microservices"],
    "postedAt": { "$date": "2025-07-21T11:44:06.616Z" },
    "__v": 0
  }
}

headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error making API call: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")