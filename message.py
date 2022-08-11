#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 12:14:38 2022

@author: efearikan
"""


class Message():
    def __init__(self):
        self._text = None
        pass

    @property
    def get(self):
        return self._text

    def format_text(self, *args):
        if (len(args) != self.get.count('{}')):
            raise ValueError("Number of args and format doesn't match!")
        self._text = self._text.format(*args)


class SuggestionMessage(Message):
    def __init__(self):
        self._text = "{} by {} \nPlaylist: {} \nPlaylist Link: {} \n{}"


class HelpMessage(Message):
    def __init__(self):
        self._text = "Mention me with \"!music\" to get a suggestion"


class QueueMessage(Message):
    def __init__(self, is_playing):
        if not is_playing:
            self._text = "Efe isn't listening to music right now! "
            + "Try again later"
        else:
            self._text = "Adding {} by {} to Efe's current queue. \n{}"


class AprrMessage(Message):
    def __init__(self):
        self._text = u"\U0001F49B" + u"\U0001F425"
