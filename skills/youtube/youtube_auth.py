import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.pickle"

def get_auth_url(redirect_uri: str):
    """Generate OAuth URL for web flow."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state

def save_credentials_from_code(auth_response_url: str, redirect_uri: str, state: str):
    """Fetch token using the callback URL."""
    # Allow HTTP transport for local testing
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=redirect_uri
    )
    flow.fetch_token(authorization_response=auth_response_url)
    credentials = flow.credentials
    
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(credentials, f)
    
    return credentials

def get_authenticated_service():
    """Get YouTube service if authenticated, otherwise raise Exception."""
    credentials = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            credentials = pickle.load(f)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(credentials, f)
        else:
            raise Exception("Unauthenticated. Please use the /auth/login endpoint to authenticate.")

    return build("youtube", "v3", credentials=credentials)