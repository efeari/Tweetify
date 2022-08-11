#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 14:04:30 2022

@author: efearikan
"""


class Track:
    def __init__(self, artist, name, url,
                 playlist_name="", playlist_link=""):
        self.artist = artist["name"]
        self.name = name
        self.url = url
        # self.img = img_url
        self.from_playlist = playlist_name
        if type(playlist_link) == dict:
            self.from_playlist_link = playlist_link["spotify"]
        else:
            self.from_playlist_link = playlist_link

    def print_track_info(self):
        print(self.name + " by " + self.artist)
        print("Playlist: " + self.from_playlist)
        print("Playlist Link: " + self.from_playlist_link)
        print(self.url)
