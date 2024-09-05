import os
import json
import google.auth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class YouTubeAPIManager:
    """
    A class to manage YouTube API interactions.
    """

    def __init__(
        self,
        credentials_file="credentials.json",
        token_file="token.json",
        scopes=("https://www.googleapis.com/auth/youtube"),
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        """
        Authenticate the user with OAuth 2.0
        """

        if os.path.exists(self.token_file):
            with open(self.token_file, "r", encoding="utf-8") as token:
                self.credentials = (
                    google.oauth2.credentials.Credentials.from_authorized_user_info(
                        json.load(token), self.scopes
                    )
                )
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes
            )
            self.credentials = flow.run_local_server(port=0)
            with open(self.token_file, "w", encoding="utf-8") as token:
                token.write(self.credentials.to_json())

        # Build the YouTube service
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )
