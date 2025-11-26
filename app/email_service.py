import os
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "onboarding@resend.dev")

def send_welcome_email(user_email: str, user_fullname: str = None):
    """Send a styled welcome email to new users using Resend"""
    
    if not RESEND_API_KEY:
        print("⚠️  Resend API key not configured. Skipping email send.")
        return False
    
    # In testing mode, send to verified email instead
    send_to_email = VERIFIED_EMAIL if VERIFIED_EMAIL else user_email
    
    if not send_to_email:
        print("⚠️  No verified email configured. Skipping email send.")
        return False
    
    try:
        # Prepare email subject and name
        subject = "Welcome to Crop Disease Identifier! 🌱"
        name_part = f" {user_fullname}" if user_fullname else ""
        
        # HTML email template with frontend green theme styling
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                        padding: 20px;
                        min-height: 100vh;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: #1f2937;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
                        border: 1px solid rgba(34, 197, 94, 0.2);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
                        padding: 50px 30px;
                        text-align: center;
                        border-bottom: 1px solid rgba(34, 197, 94, 0.2);
                    }}
                    .header h1 {{
                        color: #ffffff;
                        font-size: 32px;
                        font-weight: 700;
                        margin: 0;
                        letter-spacing: -0.5px;
                    }}
                    .header p {{
                        color: #d1fae5;
                        font-size: 14px;
                        margin: 12px 0 0 0;
                        font-weight: 400;
                    }}
                    .content {{
                        padding: 40px 30px;
                        color: #f3f4f6;
                    }}
                    .content h2 {{
                        color: #ffffff;
                        margin-top: 0;
                        font-size: 22px;
                        font-weight: 600;
                        margin-bottom: 15px;
                    }}
                    .content p {{
                        line-height: 1.7;
                        color: #d1d5db;
                        margin: 15px 0;
                        font-size: 14px;
                    }}
                    .content ol {{
                        margin: 20px 0;
                        padding-left: 20px;
                        color: #d1d5db;
                    }}
                    .content li {{
                        margin: 10px 0;
                        font-size: 14px;
                    }}
                    .feature-list {{
                        margin: 25px 0;
                        padding: 20px;
                        background: rgba(16, 185, 129, 0.1);
                        border-left: 4px solid #10b981;
                        border-radius: 6px;
                    }}
                    .feature-list p {{
                        color: #ffffff;
                        font-weight: 600;
                        margin-bottom: 12px;
                    }}
                    .feature-list ul {{
                        list-style: none;
                        padding: 0;
                        margin: 0;
                    }}
                    .feature-list li {{
                        margin: 10px 0;
                        color: #d1fae5;
                        font-size: 14px;
                        padding-left: 20px;
                        position: relative;
                    }}
                    .feature-list li:before {{
                        content: "✓";
                        position: absolute;
                        left: 0;
                        color: #10b981;
                        font-weight: bold;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white;
                        padding: 14px 40px;
                        text-decoration: none;
                        border-radius: 8px;
                        margin: 25px 0;
                        font-weight: 600;
                        transition: all 0.3s;
                        border: 1px solid #10b981;
                        font-size: 15px;
                    }}
                    .button:hover {{
                        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
                        transform: translateY(-2px);
                        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
                    }}
                    .divider {{
                        height: 1px;
                        background: rgba(34, 197, 94, 0.2);
                        margin: 30px 0;
                    }}
                    .footer {{
                        background: rgba(5, 150, 105, 0.1);
                        padding: 25px 30px;
                        text-align: center;
                        color: #9ca3af;
                        font-size: 12px;
                        border-top: 1px solid rgba(34, 197, 94, 0.2);
                    }}
                    .footer p {{
                        margin: 6px 0;
                        color: #9ca3af;
                    }}
                    .footer strong {{
                        color: #d1fae5;
                    }}
                    .highlight {{
                        color: #10b981;
                        font-weight: 600;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌱 Crop Disease Identifier</h1>
                        <p>Your Agricultural Companion</p>
                    </div>
                    
                    <div class="content">
                        <h2>Welcome to the Family! 🎉</h2>
                        <p>Hi <span class="highlight">{user_fullname or 'there'}</span>,</p>
                        
                        <p>We're thrilled to have you join our community! <strong>Crop Disease Identifier</strong> is your trusted AI-powered companion for identifying and managing crop diseases with precision and ease.</p>
                        
                        <div class="feature-list">
                            <p>What you can do:</p>
                            <ul>
                                <li>📸 Capture and upload leaf images instantly</li>
                                <li>🔍 Get AI-powered disease identification</li>
                                <li>💡 Receive evidence-based treatment recommendations</li>
                                <li>📊 Monitor crop health over time</li>
                                <li>🌍 Connect with a global farming community</li>
                            </ul>
                        </div>
                        
                        <h2 style="margin-top: 30px; font-size: 18px;">Getting Started is Simple:</h2>
                        <ol>
                            <li><strong>Log in</strong> to your account</li>
                            <li><strong>Upload</strong> an image of your crop</li>
                            <li><strong>Get instant</strong> disease diagnosis</li>
                            <li><strong>Apply</strong> recommended treatment</li>
                        </ol>
                        
                        <p>Have questions? Our support team is here to help. Feel free to reach out anytime.</p>
                        
                        <div style="text-align: center;">
                            <a href="http://localhost:3000/dashboard" class="button">Get Started Now</a>
                        </div>
                        
                        <div class="divider"></div>
                        <p style="color: #9ca3af; font-size: 13px; font-style: italic;">
                            Best wishes for healthy crops and bountiful harvests! 🌾
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Crop Disease Identifier</strong></p>
                        <p>Powered by AI for Agriculture</p>
                        <p style="margin-top: 12px; border-top: 1px solid rgba(34, 197, 94, 0.2); padding-top: 12px;">
                            © 2025 All rights reserved. | support@cropdiseaseidentifier.com
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        text = f"""Welcome{name_part}!

Thank you for joining Crop Disease Identifier. We're excited to have you on board!

What you can do:
- Capture and upload leaf images instantly
- Get AI-powered disease identification
- Receive evidence-based treatment recommendations
- Monitor crop health over time
- Connect with a global farming community

Getting started is simple:
1. Log in to your account
2. Upload an image of your crop
3. Get instant disease diagnosis
4. Apply recommended treatment

Have questions? Our support team is here to help.

Best wishes for healthy crops and bountiful harvests!

© 2025 Crop Disease Identifier. All rights reserved.
support@cropdiseaseidentifier.com
"""
        
        # Send email via Resend API
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": EMAIL_FROM,
            "to": user_email,
            "subject": subject,
            "html": html,
            "text": text
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
                print(f"✅ Welcome email sent successfully to {user_email}")
        else:
            print(f"❌ Failed to send email. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False
