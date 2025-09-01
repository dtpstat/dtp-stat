import logging
import requests
from constance import config
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, message):
    token = config.DONATES_TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message,
    }
    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
        logger.info(f"Successfully sent message to {chat_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to {chat_id}: {e}")


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveUploader:
    """
    A class to handle uploading files to Google Drive.
    """

    def __init__(self):
        self.creds = None
        # Try to get credentials from CONSTANCE_CONFIG
        try:
            # Get credentials from constance config
            creds_data = json.loads(config.DONATES_GOOGLE_CREDENTIALS)
            flow = InstalledAppFlow.from_client_config(creds_data, SCOPES)
            self.creds = flow.run_local_server(port=0)
            
            # Save credentials to constance config
            config.DONATES_GOOGLE_TOKEN = self.creds.to_json()
        except (json.JSONDecodeError, AttributeError):
            # If we can't get credentials from constance, try to use existing token
            try:
                token_data = json.loads(config.DONATES_GOOGLE_TOKEN)
                self.creds = Credentials.from_authorized_user_info(token_data, SCOPES)
                
                # Refresh if expired
                if self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    # Save refreshed credentials
                    config.DONATES_GOOGLE_TOKEN = self.creds.to_json()
            except (json.JSONDecodeError, AttributeError):
                logger.error("No valid Google Drive credentials found in CONSTANCE_CONFIG")
                raise Exception("No valid Google Drive credentials found")

        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, file_path, folder_id=None):
        """
        Uploads a file to Google Drive.

        Args:
            file_path (str): The path to the file to upload.
            folder_id (str, optional): The ID of the folder to upload the file to. Defaults to None.

        Returns:
            str: The ID of the uploaded file.
        """
        file_metadata = {'name': os.path.basename(file_path)}
        if folder_id:
            file_metadata['parents'] = [folder_id]  # Note: should be a list

        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
        ).execute()
        return file.get('id')
