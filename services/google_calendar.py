import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import SCOPES

def get_calendar_service(creds_json_str: str):
    # восстановление сессии и обновление токена
    creds_data = json.loads(creds_json_str)
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        
    service = build('calendar', 'v3', credentials=creds)
    return service, creds