import google.oauth2.credentials
import googleapiclient.discovery
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

import yt_playlist.views


def get_playlists(client, request, page_token):
    try:
        if page_token:
            pass
            query = client.playlists().list(
                part='snippet,contentDetails',
                mine='true',
                pageToken=page_token,
            )
        else:
            query = client.playlists().list(
                part='snippet,contentDetails',
                mine='true',
            )

        response = query.execute()
    except RefreshError:
        request.session.clear()
        return yt_playlist.views.ListPlaylistPageView.as_view().post(request=request)
    except HttpError as http_error:
        response = http_error.resp

        # return
    except Exception as e:
        # Log Error
        raise
    finally:
        ''' Uncomment to save cookies to file
        import os
        app_root_path = settings.YT_PLAYLIST_DIR
        rel_path_playlist_items = "/tmp/mock-playlist-items.txt"
        rel_path_response = "/tmp/mock-playlists.txt"
        abs_path_playlist_item = app_root_path + rel_path_playlist_items
        abs_path_response = app_root_path + rel_path_response
        with open(abs_path_playlist_item, 'rb') as f:
            with open(abs_path_response, 'rb') as g:
                # pickle.dump(playlist_list_response, g)
                playlist_list_response = pickle.load(g)
            # pickle.dump(playlist_items, f)
            playlist_items = pickle.load(f)
        '''

        return response


def get_api_client(session_credentials):
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    oauth_creds = google.oauth2.credentials.Credentials(
        **session_credentials)
    client = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=oauth_creds)
    return client


def create_playlist(client, request_title, request):
    try:
        response = client.playlists().insert(
            part="snippet",
            body=dict(
                snippet=(dict(title=request_title))
            ), ) \
            .execute()
    except RefreshError:
        return yt_playlist.views.ListPlaylistPageView.as_view().post(request=request)
    except HttpError as http_error:
        response = http_error.resp
    except Exception as e:
        # Log Error
        raise
    finally:
        ''' Uncomment to save cookies to file
        import os
        app_root_path = settings.YT_PLAYLIST_DIR
        rel_path_response = "/tmp/mock-response.txt"
        abs_path_response = app_root_path + rel_path_response
        with open(abs_path_response, 'rb') as f:
            # pickle.dump(response, f)
            response = pickle.load(f)
        '''
    return response


def get_channel_name(client, request):
    try:
        response = client.channels().list(
            part='snippet',
            mine=True,
        ).execute()
    except RefreshError:
        request.session.clear()
        return yt_playlist.views.ListPlaylistPageView.as_view().post(request=request)
    finally:
        return response


def get_user_name(client, request):
    try:
        response = client.channels().list(
            part="snippet",
            mine=True,
        ) \
            .execute()
    except RefreshError:
        request.session.clear()
        return yt_playlist.views.ListPlaylistPageView.as_view().post(request=request)
    except HttpError as http_error:
        response = http_error.resp
        # Handle this error somehow
    except Exception as e:
        raise
    finally:
        return response


def upload_to_playlist(client, request, playlist_id, video_id, playlist_index):
    try:
        response = client.playlistItems().insert(
            part="snippet",
            # body=resource,
            body=dict(
                snippet=dict(
                    playlistId=playlist_id,
                    resourceId=dict(
                        videoId=video_id,
                        kind="youtube#video"
                    ),
                    position=str(playlist_index),
                )
            )
        ) \
            .execute()

    except RefreshError:
        request.session.clear()
        return yt_playlist.views.ListPlaylistPageView.as_view().post(request=request)
    except HttpError as http_error:
        response = http_error.resp
        # Handle this error somehow
    except Exception as e:
        # Log Error
        raise
    finally:
        ''' Uncomment to save cookies to file
        import os

        app_root_path = settings.YT_PLAYLIST_DIR
        rel_path_response = "/tmp/mock-response.txt"
        abs_path_response = app_root_path + rel_path_response
        with open(abs_path_response, 'rb') as f:
            # pickle.dump(response, f)
            response = pickle.load(f)
        '''
        return response
