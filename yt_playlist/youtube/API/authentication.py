import json
import os

import google_auth_oauthlib.flow
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

app_root_path = settings.YT_PLAYLIST_DIR

# If local machine, use client_secret file, if prod use config_var
# i.e. Parse client_secret string to json, if fails, set the local variable and conditional "client_secret_config_var".
try:
    client_secret_config_var = json.loads(os.environ.get('client_secret_google_api', None))
except TypeError:
    client_secret_config_var = None
    client_secret = app_root_path + "/tmp/client_secret.json"


API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/youtube",
]


def oath_2_callback(request):
    if client_secret_config_var:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_secret_config_var,
            scopes=None,
            state=request.session["state"]
        )
    else:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file=client_secret,
            scopes=None,
            state=request.session["state"]
        )

    flow.redirect_uri = get_oauth_callback_redirect_uri(request)

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


def get_oauth_callback_redirect_uri(request):
    return request.scheme + "://" + request.get_host() + '/oauth2callback/'


def get_authorization_url_with_flow(request):
    if client_secret_config_var:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_secret_config_var,
            scopes=scopes,
        )
    else:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file=client_secret,
            scopes=scopes)
    flow.redirect_uri = get_oauth_callback_redirect_uri(request)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    request.session["state"] = state
    return authorization_url
