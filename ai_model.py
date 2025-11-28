import os
import json
from google import generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_GENERATIVE_AI_API_KEY"))

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def get_gemini_treatment(detection_result):
    """Generate treatment and care recommendations using Gemini AI based on detection results."""
    try:
        prompt = """
You are an expert agricultural consultant AI.
I have a plant disease analysis result:

"""
        prompt += json.dumps(detection_result, indent=2)
        
        prompt += """

Please analyze this information and provide a refined, user-friendly diagnosis.
Your output MUST be a valid JSON object with the following structure:
{
    "predicted_class": "The name of the disease (refined if necessary)",
    "symptoms": ["List of clear, observable symptoms"],
    "treatment": ["Step-by-step treatment recommendations"],
    "prevention": ["Preventive measures for the future"],
    "expert_advice": "A brief, encouraging expert tip"
}

Do not include any markdown formatting (like ```json ... ```). Just the raw JSON string.
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Clean up response if it contains markdown
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())

    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        # Fallback to the original detection result if Gemini fails
        return {
            "predicted_class": detection_result.get("disease_name", "Unknown"),
            "symptoms": detection_result.get("symptoms", []),
            "treatment": detection_result.get("treatment", []),
            "prevention": detection_result.get("possible_causes", []),
            "expert_advice": "Please consult a local agricultural expert."
        }
