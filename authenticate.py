import os
import json
import google.auth
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

load_dotenv()


class YouTubeAPIManager:
    """
    A class to manage YouTube API interactions.
    """

    def __init__(
        self,
        credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
        token_file=os.getenv("GOOGLE_TOKEN_FILE", "token.json"),
        scopes=("https://www.googleapis.com/auth/youtube"),
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        """
        Authenticate the user with OAuth 2.0 and refresh the token if expired.
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, "r", encoding="utf-8") as token:
                info = json.load(token)
                self.credentials = (
                    google.oauth2.credentials.Credentials.from_authorized_user_info(
                        info, self.scopes
                    )
                )

            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                try:
                    self.credentials.refresh(google.auth.transport.requests.Request())
                    with open(self.token_file, "w", encoding="utf-8") as token:
                        token.write(self.credentials.to_json())
                    print("Token refreshed successfully.")
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self._run_auth_flow()
            elif not self.credentials.valid:
                self._run_auth_flow()
        else:
            self._run_auth_flow()

        # Build the YouTube service
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

    def _run_auth_flow(self):
        """
        Runs the OAuth 2.0 flow and saves new credentials to the token file.
        """
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.scopes
        )
        self.credentials = flow.run_local_server(port=0)

        with open(self.token_file, "w", encoding="utf-8") as token:
            token.write(self.credentials.to_json())
        print("New token obtained and saved.")
