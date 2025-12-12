"""Gmail API integration module.

Provides connection and data fetching capabilities for Gmail using
the Google Gmail API with OAuth 2.0 authentication.
"""

import logging
import os
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logging.warning("Google API libraries not installed. Gmail functionality will be limited.")

logger = logging.getLogger(__name__)


class GmailConnector:
    """Gmail API connector for fetching and managing emails.
    
    Handles OAuth 2.0 authentication and provides methods to:
    - Fetch emails with various filters
    - Get email details
    - Create and manage labels
    - Apply filters
    """
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json', 
                 token_file: str = 'token.pickle',
                 config: Optional[Dict[str, Any]] = None):
        """Initialize Gmail connector.
        
        Args:
            credentials_file: Path to OAuth 2.0 credentials JSON file
            token_file: Path to store/load authentication token
            config: Optional configuration dictionary
        """
        if not GMAIL_AVAILABLE:
            raise ImportError("Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.config = config or {}
        
        gmail_config = self.config.get('gmail', {})
        self.scopes = gmail_config.get('scopes', self.SCOPES)
        self.max_results = gmail_config.get('max_results', 1000)
        self.batch_size = gmail_config.get('batch_size', 100)
        
        self.service = None
        self.creds = None
        
        logger.info("GmailConnector initialized")
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API.
        
        Returns:
            True if authentication successful
        """
        try:
            # Load existing token
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If no valid credentials, authenticate
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Credentials file not found: {self.credentials_file}. "
                            "Please download it from Google Cloud Console."
                        )
                    
                    logger.info("Starting OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build service
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def fetch_emails(self, max_results: Optional[int] = None,
                    query: str = '', 
                    label_ids: Optional[List[str]] = None,
                    after_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., 'from:example@gmail.com')
            label_ids: List of label IDs to filter by
            after_date: Only fetch emails after this date
        
        Returns:
            List of email dictionaries
        """
        if not self.service:
            if not self.authenticate():
                logger.error("Cannot fetch emails: authentication failed")
                return []
        
        max_results = max_results or self.max_results
        emails = []
        
        try:
            # Build query
            if after_date:
                date_str = after_date.strftime('%Y/%m/%d')
                query += f" after:{date_str}"
            
            logger.info(f"Fetching emails with query: '{query}'")
            
            # List messages
            page_token = None
            while len(emails) < max_results:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    labelIds=label_ids,
                    maxResults=min(self.batch_size, max_results - len(emails)),
                    pageToken=page_token
                ).execute()
                
                messages = results.get('messages', [])
                
                if not messages:
                    break
                
                # Fetch full message details
                for message in messages:
                    email_data = self._fetch_message_details(message['id'])
                    if email_data:
                        emails.append(email_data)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            logger.info(f"Fetched {len(emails)} emails")
            return emails
            
        except HttpError as error:
            logger.error(f"Error fetching emails: {error}")
            return emails
    
    def _fetch_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed information for a specific message."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Parse date
            date_str = headers.get('Date', '')
            try:
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_str)
            except:
                date = datetime.now()
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'sender': headers.get('From', ''),
                'subject': headers.get('Subject', ''),
                'date': date,
                'body': body,
                'labels': message.get('labelIds', []),
                'size': int(message.get('sizeEstimate', 0)),
                'snippet': message.get('snippet', '')
            }
            
        except HttpError as error:
            logger.warning(f"Error fetching message {message_id}: {error}")
            return None
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from message payload."""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
                elif 'parts' in part:
                    body = self._extract_body(part)
                    if body:
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        
        return body
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all Gmail labels.
        
        Returns:
            List of label dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            logger.info(f"Retrieved {len(labels)} labels")
            return labels
        except HttpError as error:
            logger.error(f"Error fetching labels: {error}")
            return []
    
    def create_label(self, label_name: str) -> Optional[str]:
        """Create a new Gmail label.
        
        Args:
            label_name: Name for the new label
        
        Returns:
            Label ID if successful, None otherwise
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            label = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            result = self.service.users().labels().create(
                userId='me',
                body=label
            ).execute()
            
            logger.info(f"Created label: {label_name}")
            return result['id']
            
        except HttpError as error:
            logger.error(f"Error creating label: {error}")
            return None
    
    def apply_filter(self, filter_config: Dict[str, Any]) -> bool:
        """Apply a filter to Gmail.
        
        Args:
            filter_config: Filter configuration with criteria and actions
        
        Returns:
            True if successful
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            result = self.service.users().settings().filters().create(
                userId='me',
                body=filter_config
            ).execute()
            
            logger.info(f"Applied filter: {result['id']}")
            return True
            
        except HttpError as error:
            logger.error(f"Error applying filter: {error}")
            return False
    
    def modify_message(self, message_id: str, 
                      add_labels: Optional[List[str]] = None,
                      remove_labels: Optional[List[str]] = None) -> bool:
        """Modify labels on a message.
        
        Args:
            message_id: ID of the message to modify
            add_labels: List of label IDs to add
            remove_labels: List of label IDs to remove
        
        Returns:
            True if successful
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            return True
            
        except HttpError as error:
            logger.error(f"Error modifying message: {error}")
            return False
