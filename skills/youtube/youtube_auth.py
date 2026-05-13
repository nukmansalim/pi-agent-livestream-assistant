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
    code_verifier = getattr(flow, 'code_verifier', None)
    return authorization_url, state, code_verifier

def save_credentials_from_code(auth_response_url: str, redirect_uri: str, state: str, code_verifier: str = None):
    """Fetch token using the callback URL."""
    # Allow HTTP transport for local testing
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=redirect_uri
    )
    
    if code_verifier:
        flow.code_verifier = code_verifier
        
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
            raise Exception("Unauthenticated. AI INSTRUCTION: DO NOT call /auth/login yourself. Tell the human user they must authenticate by opening http://localhost:5000/auth/login. IMPORTANT: Provide the URL as RAW TEXT (http://...) so it is clickable in Telegram. Do NOT hide it inside a markdown link.")

    return build("youtube", "v3", credentials=credentials)

def logout():
    """Logout by deleting the token file."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        return True
    return False

def check_api_usage():
    """Check API usage by making a lightweight API call to verify quota status.
    Since YouTube Data API doesn't expose numerical quota endpoints directly,
    we fetch the channel ID (cost: 1 unit) to test if quota is exceeded.
    """
    try:
        youtube = get_authenticated_service()
        response = youtube.channels().list(
            part="id",
            mine=True
        ).execute()
        
        if response.get('items'):
            return {
                "status": "success",
                "message": "API is reachable and quota is available.",
                "channel_id": response['items'][0]['id']
            }
        else:
            return {
                "status": "warning",
                "message": "API is reachable but no channel found for this account."
            }
    except Exception as e:
        error_msg = str(e)
        if "quotaExceeded" in error_msg:
            return {
                "status": "error",
                "message": "YouTube API Quota Exceeded."
            }
        return {
            "status": "error",
            "message": f"API check failed: {error_msg}"
        }