# app.py

import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from dotenv import dotenv_values
import requests # Import the requests library for direct HTTP calls

# --- Load environment variables from .env file ---
config = dotenv_values(".env")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file. "
        "Please create a .env file in the same directory as app.py "
        "and add GEMINI_API_KEY=\"YOUR_ACTUAL_API_KEY\" to it."
    )

app = Flask(__name__)

# Define the Gemini Embedding API endpoint
GEMINI_EMBEDDING_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
)
GEMINI_MODEL = 'gemini-2.5-flash'
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


@app.route('/generate_job_description', methods=['POST'])
def generate_job_description():
    user_prompt = request.json.get('prompt')

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"As an expert HR professional, generate a comprehensive and engaging job description based on the following details. Include sections like Job Title, Responsibilities, Qualifications, and Benefits. Make it suitable for an online job board:\n\n'{user_prompt}'"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        gemini_response = response.json()
        
        # Extract the generated text from the Gemini response
        job_description = ""
        if "candidates" in gemini_response and gemini_response["candidates"]:
            for part in gemini_response["candidates"][0]["content"]["parts"]:
                if "text" in part:
                    job_description += part["text"]

        if job_description:
            return jsonify({"job_description": job_description})
        else:
            return jsonify({"error": "Failed to generate job description from Gemini API. Response may be empty or malformed."}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Gemini API: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500






def get_embedding(text):
    """
    Generates an embedding vector for the given text by making a direct
    HTTP POST request to the Gemini Embedding API.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY # API key in header
    }

    payload = {
        "content": {
            "parts": [
                {"text": text}
            ]
        },
        "task_type": "SEMANTIC_SIMILARITY"
    }

    try:
        # Make the POST request to the Gemini Embedding API
        response = requests.post(GEMINI_EMBEDDING_API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        response_data = response.json()
        if 'embedding' in response_data and 'values' in response_data['embedding']:
            return np.array(response_data['embedding']['values'])
        else:
            app.logger.error(f"Unexpected embedding response structure: {response_data}")
            return None
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error making API call to Gemini Embedding service: {e}")
        return None
    except json.JSONDecodeError:
        app.logger.error(f"Failed to decode JSON from Gemini Embedding response: {response.text}")
        return None
    except Exception as e:
        app.logger.error(f"An unexpected error occurred in get_embedding: {e}")
        return None

def calculate_match_score(candidate_text, job_text):
    """
    Calculates a matchmaking score between candidate and job description
    using Gemini embeddings and cosine similarity.
    """
    candidate_vector = get_embedding(candidate_text)
    job_vector = get_embedding(job_text)

    if candidate_vector is None or job_vector is None:
        return None, "Failed to generate embeddings. Please check API key, network, or input text."

    # Reshape vectors for sklearn's cosine_similarity function (expects 2D arrays)
    candidate_vector_reshaped = candidate_vector.reshape(1, -1)
    job_vector_reshaped = job_vector.reshape(1, -1)

    # Calculate cosine similarity
    score = cosine_similarity(candidate_vector_reshaped, job_vector_reshaped)[0][0]

    interpretation = ""
    if score >= 0.85:
        interpretation = "Excellent Match! This candidate is highly aligned with the job requirements."
    elif score >= 0.70:
        interpretation = "Strong Match. This candidate has many of the required skills and experiences."
    elif score >= 0.50:
        interpretation = "Moderate Match. There are some overlaps, but also areas for improvement or further review."
    else:
        interpretation = "Low Match. The candidate's profile does not strongly align with the job description."

    return score, interpretation








@app.route('/match', methods=['POST'])
def match_api():
    """
    API endpoint to calculate matchmaking score from JSON input.
    Expects a JSON body with 'candidate_details' and 'job_description' fields.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON or empty request body."}), 400

    candidate_data = data.get('candidate_details')
    job_data = data.get('job_description')

    if not candidate_data:
        return jsonify({"error": "Missing 'candidate_details' in JSON payload."}), 400
    if not job_data:
        return jsonify({"error": "Missing 'job_description' in JSON payload."}), 400

    # --- Extract and combine relevant text from JSON for Job Description ---
    job_description_parts = []
    if 'jobDescription' in job_data and job_data['jobDescription']:
        job_description_parts.append(job_data['jobDescription'])
    if 'responsibilities' in job_data and job_data['responsibilities']:
        job_description_parts.append(job_data['responsibilities'])
    if 'keySkills' in job_data and job_data['keySkills']:
        if isinstance(job_data['keySkills'], list):
            job_description_parts.extend(job_data['keySkills'])
        else:
            app.logger.warning(f"job_data['keySkills'] is not a list: {job_data['keySkills']}")
    job_text_for_embedding = " ".join(job_description_parts)

    # --- Extract and combine relevant text from JSON for Candidate Details ---
    candidate_profile_parts = []
    if 'self_intro' in candidate_data and candidate_data['self_intro']:
        candidate_profile_parts.append(candidate_data['self_intro'])
    if 'Work Experience' in candidate_data and candidate_data['Work Experience']:
        candidate_profile_parts.append(candidate_data['Work Experience'])
    if 'skills' in candidate_data and candidate_data['skills']:
        if isinstance(candidate_data['skills'], list):
            candidate_profile_parts.extend(candidate_data['skills'])
        else:
            app.logger.warning(f"candidate_data['skills'] is not a list: {candidate_data['skills']}")
    if 'Tools' in candidate_data and candidate_data['Tools']:
        if isinstance(candidate_data['Tools'], list):
            candidate_profile_parts.extend(candidate_data['Tools'])
        else:
            app.logger.warning(f"candidate_data['Tools'] is not a list: {candidate_data['Tools']}")

    candidate_text_for_embedding = " ".join(candidate_profile_parts)

    if not job_text_for_embedding or not candidate_text_for_embedding:
        return jsonify({
            "error": "Extracted text for embedding is empty. "
                     "Please ensure relevant fields (jobDescription, responsibilities, keySkills for job; "
                     "self_intro, Work Experience, skills, Tools for candidate) are present and contain text in the JSON."
        }), 400

    score, interpretation = calculate_match_score(candidate_text_for_embedding, job_text_for_embedding)

    if score is None:
        return jsonify({"error": interpretation}), 500

    return jsonify({
        "match_score": round(score, 4),
        "interpretation": interpretation
    })

if __name__ == '__main__':
    app.run(debug=True)

