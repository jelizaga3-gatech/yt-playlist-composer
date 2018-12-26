from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import generic

from yt_playlist.popo import form_selection
from yt_playlist.youtube.API import authentication, playlist, helper


def context_save_username(request, session_credentials, context):
    client = playlist.get_api_client(session_credentials)
    response = playlist.get_user_name(client=client, request=request)
    context["username"] = response["items"][0]["snippet"]["title"]


def context_save_playlist_meta(request, playlist_item):
    request.session["playlist_id"] = playlist_item["item_id"]
    request.session["playlist_title"] = playlist_item["name"]


class InstructionPageView(generic.TemplateView):
    template_name = "instructions.html"


class LoginPageView(generic.TemplateView):
    template_name = "yt-login.html"

    def get(self, request, **kwargs):
        context = {}
        if request.session.__contains__("credentials"):

            session_credentials_ = request.session["credentials"]

            context_save_username(request, session_credentials_, context)

            context["credentials"] = session_credentials_
        else:
            context = None

        return TemplateResponse(request=request, template=self.template_name, context=context)

    def post(self, request):
        post_type = request.POST
        if "yt-list-playlist" in post_type:
            return redirect(reverse("list_playlist"))
        elif "yt-upload-playlist" in post_type:
            return redirect(reverse("add_playlist_item"))
        authorization_url = authentication.get_authorization_url_with_flow(request)

        return redirect(authorization_url)


class ListPlaylistPageView(generic.TemplateView):
    template_name = 'yt-list-playlist.html'

    def get(self, request, **kwargs):
        context = dict(list_exist=False)
        if request.session.__contains__("credentials"):
            session_credentials_ = request.session["credentials"]
            context.update(credentials=session_credentials_)

            context_save_username(request=request, session_credentials=session_credentials_, context=context)

            self.get_playlist_items(request=request, session_credentials=session_credentials_, context=context,
                                    page_token=None)

        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        context = dict(list_exist=False)
        if request.session.__contains__("credentials"):
            session_credentials = request.session['credentials']
            context.update(credentials=session_credentials)
            post_type = request.POST

            if "get-list" in post_type or 'next-list' in post_type or 'prev-list' in post_type:

                next_val = request.POST.get('next-list', )
                prev_val = request.POST.get('prev-list', )

                if next_val or prev_val:
                    page_token = next_val or prev_val
                else:
                    page_token = None

                context_save_username(request=request, session_credentials=session_credentials, context=context)

                self.get_playlist_items(request, session_credentials, context, page_token)

                return render(request, template_name=self.template_name, context=context)

            elif "add-list" in post_type:
                return redirect(reverse("list_playlist/add"))

            elif "add-items" in post_type:

                radio_value = int(request.POST["playlist_radio"])
                form = request.session["form"]

                playlist_item_generator = filter(lambda x: x["radio_value"] == radio_value, form)
                playlist_item = next(playlist_item_generator)

                context_save_playlist_meta(request=request, playlist_item=playlist_item)

                return redirect(reverse("add_playlist_item"))

        return render(request, template_name=self.template_name, context=context)

    def get_playlist_items(self, request, session_credentials, context, page_token):
        client = playlist.get_api_client(session_credentials)
        playlist_list_response = playlist.get_playlists(client=client, request=request, page_token=page_token)
        playlist_items = playlist_list_response["items"]
        playlist_form_items = []
        for playlist_item in playlist_items:
            item = dict(name=playlist_item["snippet"].get("title", ).ljust(10),
                        playlist_item_count=playlist_item["contentDetails"].get("itemCount", ),
                        radio_value=len(playlist_form_items),
                        item_id=playlist_item["id"])
            form_selection.YouTubeItems(item)
            playlist_form_items.append(item)
        context["list_exist"] = True
        context["next_token"] = playlist_list_response.get("nextPageToken", )
        context["prev_token"] = playlist_list_response.get("prevPageToken", )
        if playlist_form_items:
            context["form"] = playlist_form_items
            request.session["form"] = playlist_form_items


class AddPlaylistPageView(generic.TemplateView):
    template_name = "yt-add-playlist.html"

    def get(self, request, *args, **kwargs):
        context = {}
        if request.session.__contains__("credentials"):
            # Check for Valid Yt User
            session_credentials_ = request.session["credentials"]
            context.update(credentials=session_credentials_)

            response_key = "insert_playlist_response"
            if response_key in request.session:
                valid_request = request.session.pop("add-playlist-flag", None)
                if not valid_request:
                    return redirect(reverse("yt_login"))
                response = request.session.pop(response_key)
                context[response_key] = response

                playlist_id = response.get("id", )
                title = response.get("snippet", ).get("title", )

                playlist_dict = dict(playlist_id=playlist_id, title=title, )
                context.update(playlist_dict)

                playlist_item = dict(item_id=playlist_id, name=title)
                context_save_playlist_meta(request=request, playlist_item=playlist_item)
            else:
                # Get Client
                client = playlist.get_api_client(session_credentials=session_credentials_)

                # Get Channel Name
                channel_response = playlist.get_channel_name(client, request)
                if channel_response.get("pageInfo", ).get("totalResults", ) > 1:
                    raise ValueError("You have too many channels associated with this account.")
                context["channel_name"] = channel_response.get("items", )[0].get("snippet", ).get("title", )

                # Save username to context
                context_save_username(request=request, session_credentials=session_credentials_, context=context)

            return render(request, template_name=self.template_name, context=context)
        else:
            return redirect("yt_login")

    def post(self, request):
        context = {}
        # Authenticate User
        if request.session.__contains__("credentials"):
            session_credentials_ = request.session["credentials"]
            context["credentials"] = session_credentials_
            client = playlist.get_api_client(session_credentials_)

            # Get Title
            if "submit_" in request.POST:
                request_title = request.POST.get("request_title", )

                title_len = len(request_title)
                if title_len <= 4 or title_len >= 25:
                    msg = "You inputted the string: '{0}'. The title must be between 5 to 25 chars long. You can rename it " \
                          "later on YouTube.".format(request_title)
                    context["credentials"] = None
                    context["error_message"] = msg
                    return render(request, template_name=self.template_name, context=context)

                # Send Request
                response = playlist.create_playlist(client, request_title, request)

                # Handle Response
                request.session["insert_playlist_response"] = response

                request.session["add-playlist-flag"] = True

                return redirect(request.path)
            elif 'view_all_playlists' in request.POST:
                return redirect("list_playlist")
            elif 'add_item_to_playlist' in request.POST:

                return redirect("add_playlist_item")

        else:
            raise RuntimeError("Unexpected flow in AddPlaylistView.")


class AddPlaylistItemsPageView(generic.TemplateView):
    template_name = "yt-add-items-playlist.html"

    def get(self, request, *args, **kwargs):
        context = {}
        if request.session.__contains__("credentials"):
            # Check for Valid Yt User
            session_credentials_ = request.session["credentials"]
            context.update(credentials=session_credentials_)
            self.context_display_username_playlist(context, request, session_credentials_)
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        context = {}
        # Authenticate User
        if request.session.__contains__("credentials"):
            session_credentials_ = request.session["credentials"]
            context["credentials"] = session_credentials_
            client = playlist.get_api_client(session_credentials_)

            if 'upload_items' in request.POST:
                text_area_input = request.POST.get("text_area_input", )
                videos = []
                read_lines = text_area_input.split('\r\n')
                if not read_lines[0].strip():
                    context["validation_error"] = "The field below cannot be empty. See instructions above."
                    self.context_display_username_playlist(context, request, session_credentials_)
                    return render(request, template_name=self.template_name, context=context)
                for line in read_lines:
                    if line.strip():
                        try:
                            playlist_index, video_id_str = None, None

                            line_split = line.split("-", 1)
                            stripped_index = line_split[0].strip()
                            playlist_index = int(stripped_index)
                            raw_video_id = line_split[1].strip().rstrip(',')
                            video_id_str = helper.video_id(raw_video_id)
                        except (ValueError, IndexError):
                            context[
                                "validation_error"] = "Videos could not be parsed. Please read the instructions carefully or try again."
                            self.context_display_username_playlist(context, request, session_credentials_)
                            return render(request, template_name=self.template_name, context=context)
                        except Exception:
                            print("Unexpected error occurred!")
                            raise
                        finally:
                            if playlist_index and video_id_str:
                                videos.append(dict(playlist_index=playlist_index, video_id=video_id_str))
                playlist_id_1 = request.POST.get("playlist-id-1", )
                playlist_id_2 = request.POST.get("playlist-id-2", )
                playlist_id = playlist_id_1 or playlist_id_2
                context["playlist_id"] = playlist_id
                responses = []
                for video in videos:
                    upload_video_id = video.get("video_id")
                    upload_playlist_index = video.get("playlist_index") - 1
                    response = playlist.upload_to_playlist(client=client,
                                                           request=request,
                                                           playlist_id=playlist_id,
                                                           video_id=upload_video_id,
                                                           playlist_index=upload_playlist_index)
                    responses.append(response)

                context["responses"] = responses

                self.context_display_username_playlist(context, request, session_credentials_)
            return render(request, template_name=self.template_name, context=context)
        else:
            return redirect("yt_login")

    def context_display_username_playlist(self, context, request, session_credentials_):
        context_save_username(request=request, session_credentials=session_credentials_,
                              context=context)
        context["playlist_item_id"] = request.session.get("playlist_id", )
        context["playlist_title"] = request.session.get("playlist_title", )

        video_ids = "1 - M7FIvfx5J10, \n" + "3 - https://www.youtube.com/watch?v=M7FIvfx5J10  "
        context.update(video_ids=video_ids)
