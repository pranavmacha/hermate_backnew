import json
import os
import logging
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=API_KEY)

AGENT_SYSTEM_PROMPT = """
You are an assistant for a menstrual health app called HerMate.

Your job:
- Understand the user’s symptoms, mood, flow, sleep, and energy.
- Give supportive, general advice only.
- DO NOT diagnose any condition.
- DO NOT prescribe any medicine or dosage.
- Keep tone calm, friendly, and non-judgmental.
- If symptoms are severe (fainting, chest pain, suicidal thoughts, extremely heavy bleeding), advise to seek medical care.

Output MUST be valid JSON using this schema:

{
  "summary": string,
  "severity_level": "low" | "medium" | "high",
  "foods_to_eat": string[],
  "foods_to_avoid": string[],
  "home_remedies": string[],
  "activities_to_do": string[],
  "activities_to_avoid": string[],
  "when_to_see_doctor": string[],
  "emotional_support": string[],
  "safety_message": string
}

Rules:
- summary = 2–4 lines
- severity_level = your judgement of how concerning the symptoms sound
- when_to_see_doctor must be [] when symptoms are mild
- safety_message must ALWAYS be present
- Never use markdown, ONLY pure JSON.
"""

def build_user_prompt(payload):
    return f"""
User symptom data:

- Symptoms list: {payload['symptoms']}
- Severity: {payload['severity']}
- Cycle day: {payload['cycle_day']}
- Notes: {payload['notes']}

Output strictly JSON.
"""

def generate_symptom_advice(payload):
    """Generate personalized symptom advice using Google Generative AI.
    
    Args:
        payload (dict): Validated symptom data with keys: symptoms, severity, cycle_day, notes
        
    Returns:
        dict: Structured advice JSON or error response
    """
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=AGENT_SYSTEM_PROMPT
    )

    prompt = build_user_prompt(payload)

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
    except GoogleAPIError as e:
        logger.error(f"Google API error: {str(e)}")
        return _error_response("API service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error generating advice: {str(e)}")
        return _error_response("An unexpected error occurred")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse AI response: {raw}")
        return _error_response("Response parsing failed")

    # Ensure safety message is always present
    if "safety_message" not in data:
        data["safety_message"] = "This is general guidance, not medical advice."

    return data


def _error_response(message):
    """Generate a safe error response."""
    return {
        "summary": message,
        "severity_level": "medium",
        "foods_to_eat": [],
        "foods_to_avoid": [],
        "home_remedies": [],
        "activities_to_do": [],
        "activities_to_avoid": [],
        "when_to_see_doctor": ["If symptoms persist or worsen, please consult a healthcare provider."],
        "emotional_support": ["You're doing your best. Take slow deep breaths and rest for a moment."],
        "safety_message": "This is general guidance, not medical advice."
    }
