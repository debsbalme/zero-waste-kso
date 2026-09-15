import streamlit as st
from google_auth_oauthlib.flow import Flow


SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]


def get_google_flow(state=None):

    client_config = {
        "web": {
            "client_id":
                st.secrets["google_oauth"]["client_id"],

            "client_secret":
                st.secrets["google_oauth"]["client_secret"],

            "auth_uri":
                "https://accounts.google.com/o/oauth2/auth",

            "token_uri":
                "https://oauth2.googleapis.com/token",

            "redirect_uris": [
                st.secrets["google_oauth"]["redirect_uri"]
            ],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
    )

    flow.redirect_uri = (
        st.secrets["google_oauth"]["redirect_uri"]
    )

    return flow