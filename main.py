import os
import requests
import json
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables and strip any whitespace
ULTRAVOX_API_KEY = os.getenv("ULTRAVOX_API_KEY", "").strip()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
DESTINATION_PHONE_NUMBER = os.getenv("DESTINATION_PHONE_NUMBER", "").strip()
CORPUS_ID = os.getenv("CORPUS_ID", "").strip()

# If any required variable is empty, try manual loading
if not all([ULTRAVOX_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, 
           TWILIO_PHONE_NUMBER, DESTINATION_PHONE_NUMBER]):
    print("Standard env loading failed.")

# Ultravox call configuration
with open('prompt.txt', 'r') as file:
    SYSTEM_PROMPT = file.read()

ULTRAVOX_CALL_CONFIG = {
    "systemPrompt": SYSTEM_PROMPT,
    "model": "fixie-ai/ultravox",
    "voice": "Chinmay-English-Indian",
    "temperature": 0.3,
    "firstSpeaker": "FIRST_SPEAKER_USER",
    "medium": {"twilio": {}},
    "selectedTools":[
        { "toolName": "hangUp" },
        {
        "toolName": "queryCorpus", 
        "parameterOverrides": {
            "corpus_id": CORPUS_ID,
            "max_results": 3
        }
        }
    ]
}

ULTRAVOX_API_URL = "https://api.ultravox.ai/api/calls"

def create_ultravox_call():
    """Create a new Ultravox call configured for Twilio integration."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": ULTRAVOX_API_KEY
    }
    
    response = requests.post(
        ULTRAVOX_API_URL, 
        json=ULTRAVOX_CALL_CONFIG, 
        headers=headers
    )
    
    if response.status_code >= 400:
        raise Exception(f"Failed to create Ultravox call: {response.text}")
    
    data = response.json()
    # Extract the joinUrl from the response
    if "joinUrl" not in data:
        raise Exception(f"joinUrl not found in response: {data}")
    
    return data["joinUrl"]

def main():
    try:
        # Verify all required environment variables are set
        required_vars = {
            "ULTRAVOX_API_KEY": ULTRAVOX_API_KEY,
            "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN,
            "TWILIO_PHONE_NUMBER": TWILIO_PHONE_NUMBER,
            "DESTINATION_PHONE_NUMBER": DESTINATION_PHONE_NUMBER
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        print("Creating Ultravox call...")
        print(f"Using API key: {ULTRAVOX_API_KEY[:5]}...{ULTRAVOX_API_KEY[-5:] if len(ULTRAVOX_API_KEY) > 10 else ''}")
        join_url = create_ultravox_call()
        print(f"Got joinUrl: {join_url}")
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            twiml=f'<Response><Connect><Stream url="{join_url}"/></Connect></Response>',
            to=DESTINATION_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER
        )
        
        print(f"Call initiated: {call.sid}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()