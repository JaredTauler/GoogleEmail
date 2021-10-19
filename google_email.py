# Jared Tauler
# 9/22/21

# For typehints
from typing import Union, List

# Building raw email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode

# Files
import os.path

# Logging into google and sending messages.
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


PathLike = Union[str, bytes, os.PathLike] # For typehints.

# Main class
class resource():
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/gmail.send']

        # Gmail service
        self.service = build('gmail', 'v1', credentials=self.Creds())


    # Get credentials.
    def Creds(self,
                 token: PathLike = "token.json",
                 credentials: PathLike = 'credentials.json'
                 ):
        creds = None

        # Try reading token
        if os.path.exists(token):
            try:
                creds = Credentials.from_authorized_user_file(token, self.scope)
            except:
                creds = None

        # Make user login if no/invalid credits
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Ask user for consent
                flow = InstalledAppFlow.from_client_secrets_file(credentials, self.scope)
                creds = flow.run_local_server(port=0)

            # Save token.
            with open(token, 'w') as token:
                token.write(creds.to_json())

        # Once there are valid credits return them.
        return creds


    # Send email.
    def send(self,
            receiver: Union[str, List[str]],
            sender: str = None,
            subject: str = None,
            message_text: str = None,
            file: PathLike = None,
            filename: str = None,
            html: PathLike = None,
        ):

        Email = MIMEMultipart()
        Email["From"] = sender
        Email["To"] = receiver
        Email["Subject"] = subject

        # Attach...
        if message_text:
            Email.attach(MIMEText(message_text, "plain"))

        if html:
            with open(html, "rb") as File:
                data = File.read().decode()
                Email.attach(MIMEText(data, "html"))

        if file:
            with open(file, "rb") as File:
                Attachment = MIMEBase("application", "octet-stream")
                Attachment.set_payload(File.read())

            # If no given filename, set the filename to be that of the given file.
            if filename is None:
                filename = File.name

            # Encode file so it can be sent through,
            encoders.encode_base64(Attachment)

            Attachment.add_header(
            "Content-Disposition",
            "attachment; filename=" + filename,
            )

            Email.attach(Attachment)  # Attachment

        # Turn the email into base64. Payload for send() needs to be able to turn into json.
        raw = {'raw': urlsafe_b64encode(Email.as_bytes()).decode("utf-8")}

        try:
            # Send email
            self.service.users().messages().send(userId="me", body=raw).execute()

        except Exception as e:
            return e

        else:
            return None
