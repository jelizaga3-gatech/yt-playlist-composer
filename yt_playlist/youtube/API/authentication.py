import google_auth_oauthlib.flow
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

app_root_path = settings.YT_PLAYLIST_DIR

# These may need to be environment variables
client_secret = app_root_path + "/tmp/client_secret.json"
oauth_callback_redirect_uri = "http://127.0.0.1:8000/oauth2callback/"

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/youtube",
]


def oath_2_callback(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file=client_secret,
        scopes=None,
        state=request.session["state"])
    flow.redirect_uri = oauth_callback_redirect_uri

    flow.fetch_token(code=request.GET.__getitem__("code"))
    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(reverse("yt_login"))


def get_authorization_url_with_flow(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file=client_secret,
        scopes=scopes)
    flow.redirect_uri = oauth_callback_redirect_uri
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    request.session["state"] = state
    return authorization_url