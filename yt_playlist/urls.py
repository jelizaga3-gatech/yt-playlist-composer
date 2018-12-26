# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from yt_playlist.youtube.API import authentication
from .views import (
    InstructionPageView,
    # UdacityPageView,
    LoginPageView,
    ListPlaylistPageView,
    AddPlaylistItemsPageView,
    AddPlaylistPageView)

urlpatterns = [
    path("", InstructionPageView.as_view(), name="landing"),
    # path("udacity-parser", UdacityPageView.as_view(), name="udacity"),
    path("login/", LoginPageView.as_view(), name="yt_login"),
    path("list-playlist/", ListPlaylistPageView.as_view(), name="list_playlist"),
    path("list-playlist/add/", AddPlaylistPageView.as_view(), name="list_playlist/add"),
    path("add-playlist-item/", AddPlaylistItemsPageView.as_view(), name="add_playlist_item"),
    path("oauth2callback/", authentication.oath_2_callback, name="oath2callback")
]
