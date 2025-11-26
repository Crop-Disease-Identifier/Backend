#!/usr/bin/env python
import os
from dotenv import load_dotenv
import requests

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "onboarding@resend.dev")

print(f"API Key loaded: {bool(RESEND_API_KEY)}")
print(f"Email From: {EMAIL_FROM}")

# Test sending a simple email
headers = {
    "Authorization": f"Bearer {RESEND_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "from": EMAIL_FROM,
    "to": "zinsusezonsu@gmail.com",
    "subject": "Test Email",
    "html": "<h1>Hello from Resend!</h1>",
    "text": "Hello from Resend!"
}

try:
    response = requests.post(
        "https://api.resend.com/emails",
        headers=headers,
        json=payload,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Resend API is working correctly!")
    else:
        print("❌ Email sending failed")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
