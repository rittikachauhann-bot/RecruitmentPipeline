"""Gmail API email sender with OAuth 2.0."""

import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from config import (
    GMAIL_CREDENTIALS_FILE,
    GMAIL_TOKEN_FILE,
    GMAIL_SCOPES,
    CANDIDATE,
)

_gmail_service = None


def _get_service():
    global _gmail_service
    if _gmail_service:
        return _gmail_service

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "Gmail packages missing. Run:\n"
            "  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        )

    creds = None
    if os.path.exists(GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {GMAIL_CREDENTIALS_FILE}.\n"
                    "Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GMAIL_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    _gmail_service = build("gmail", "v1", credentials=creds)
    return _gmail_service


def send_email(to: str, subject: str, body: str, attach_cv: bool = True, include_signature: bool = True, use_html: bool = False) -> str:
    """
    Send email via Gmail API with optional portfolio signature.
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        attach_cv: Whether to attach CV file
        include_signature: Whether to include portfolio link in signature
        use_html: Whether to send as HTML (includes better formatting)
    
    Returns:
        Message ID from Gmail API
    """
    service = _get_service()

    # Import signature builder
    try:
        from email_templates import format_body_with_signature, get_footer_banner
    except ImportError:
        include_signature = False

    # Add signature if enabled
    if include_signature:
        if use_html:
            body = f"{body}{get_footer_banner()}"
        else:
            body = format_body_with_signature(body, use_html=False)

    msg = MIMEMultipart("alternative")
    msg["From"] = CANDIDATE["email"]
    msg["To"] = to
    msg["Subject"] = subject
    
    # Add both plain text and HTML parts for better compatibility
    if use_html:
        msg.attach(MIMEText(body, "plain"))
        html_body = f"<html><body><pre style='font-family: Arial, sans-serif; white-space: pre-wrap;'>{body}</pre></body></html>"
        msg.attach(MIMEText(html_body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    # Attach CV if requested and file exists
    if attach_cv and os.path.exists(CANDIDATE["cv_path"]):
        with open(CANDIDATE["cv_path"], "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        cv_filename = os.path.basename(CANDIDATE["cv_path"])
        part.add_header("Content-Disposition", f'attachment; filename="{cv_filename}"')
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    return result["id"]


def is_gmail_configured() -> bool:
    return os.path.exists(GMAIL_CREDENTIALS_FILE)
