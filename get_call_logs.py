import requests
import os 
import json
import os.path

from dotenv import load_dotenv
load_dotenv()

ULTRAVOX_API_KEY = os.getenv("ULTRAVOX_API_KEY", "").strip()

def get_call_ids(start_date, end_date):
    url = "https://api.ultravox.ai/api/calls"
    querystring = {"fromDate":start_date,"toDate":end_date}
    headers = {"X-API-Key": ULTRAVOX_API_KEY}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json().get("results")
    call_id_list = [entry.get("callId") for entry in data]
    return call_id_list

def get_stage_id(call_id):
    url = f"https://api.ultravox.ai/api/calls/{call_id}/stages"
    headers = {"X-API-Key": ULTRAVOX_API_KEY}
    response = requests.request("GET", url, headers=headers)
    data = response.json().get("results")[0]
    return data.get("callStageId")

def get_conversation_transcript(call_id, stage_id):
    url = f"https://api.ultravox.ai/api/calls/{call_id}/stages/{stage_id}/messages"
    headers = {"X-API-Key": ULTRAVOX_API_KEY}
    response = requests.request("GET", url, headers=headers)
    data = response.json().get("results")
    return data 

def convert_conversation_to_text(messages, output_file):    
    with open(output_file, 'w', encoding='utf-8') as f:
        for msg in messages:
            role = msg.get('role')
            text = msg.get('text', '')
            
            if not text:
                continue
                
            if role == 'MESSAGE_ROLE_USER':
                speaker = 'USER'
            elif role == 'MESSAGE_ROLE_AGENT':
                speaker = 'AGENT'
            else:
                continue
            
            f.write(f"{speaker}: \"{text}\"\n\n")
    
    print(f"Conversation successfully written to {output_file}")

def main(start_date, end_date):
    call_id_list = get_call_ids(start_date, end_date)
    
    directory = f"transcripts/{start_date}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for call_id in call_id_list:
        try:
            stage_id = get_stage_id(call_id)
            transcript = get_conversation_transcript(call_id, stage_id)
            output_file = f"{directory}/{call_id}.txt"
            convert_conversation_to_text(transcript, output_file)
        except Exception as e:
            print(f"Error processing call_id {call_id}: {str(e)}")

if __name__ == "__main__":
    start_date = "2025-03-31"
    end_date = "2025-03-31"
    main(start_date, end_date)