import os
from google import generativeai as genai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


SYSTEM_PROMPT = """
You are an expert agricultural consultant AI inside a FastAPI backend. 
Always provide structured, detailed, and actionable recommendations. 

Rules:
1. Always base your response on the identified crops and detected plant diseases.
2. If previous plant analysis is available, consider it for context.
3. Responses must include:
   - Plant condition
   - Immediate treatments
   - Care tips
   - When to seek professional help (max 200 words)
4. Avoid repeating information unnecessarily.
5. Use a friendly and professional tone.
6. If no diseases are detected, provide preventive care advice and monitoring tips.
"""
# x

async def get_gemini_treatment(crops, diseases):
    """Generate treatment and care recommendations using Gemini AI."""
    try:
        prompt = SYSTEM_PROMPT + "\n\n"

        if crops:
            prompt += "Identified Crops:\n"
            for crop in crops:
                prompt += f"- {crop['name']} ({crop['scientific_name']}): {crop['confidence']}% confidence\n"

        if diseases:
            prompt += "\nDetected Plant Health Issues:\n"
            for disease in diseases:
                prompt += f"- {disease['name']}: {disease['confidence']}% confidence\n"
        else:
            prompt += "\nNo diseases detected. Plant appears healthy.\n"

        prompt += """
Provide a concise and structured response following the above rules.
"""

        
        model = genai.GenerativeModel("gemini-1.5-flash")  

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        return get_basic_treatment_recommendations(crops, diseases)
