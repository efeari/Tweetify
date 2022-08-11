#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 14:04:30 2022

@author: efearikan
"""


class Track:
    def __init__(self, artist, name, url,
                 playlist_name="", playlist_link=""):
        self._artist = artist["name"]
        self._name = name
        self._url = url
        # self.img = img_url
        self._from_playlist = playlist_name
        if isinstance(playlist_link, dict):
            self._from_playlist_link = playlist_link["spotify"]
        else:
            self._from_playlist_link = playlist_link

    def print_track_info(self):
        print(self._name + " by " + self._artist)
        print("Playlist: " + self._from_playlist)
        print("Playlist Link: " + self._from_playlist_link)
        print(self._url)

    @property
    def artist(self):
        return self._artist

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def playlist(self):
        return self._from_playlist

    @property
    def playlist_link(self):
        return self._from_playlist_link
