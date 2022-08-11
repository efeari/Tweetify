#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 12:14:38 2022

@author: efearikan
"""


class Message():
    def __init__(self):
        self._text = None

    @property
    def get(self):
        return self._text

    def format_text(self, *args):
        if len(args) != self.get.count('{}'):
            raise ValueError("Number of args and format doesn't match!")
        self._text = self._text.format(*args)


class SuggestionMessage(Message):
    def __init__(self):
        super().__init__()
        self._text = "{} by {} \nPlaylist: {} \nPlaylist Link: {} \n{}"


class HelpMessage(Message):
    def __init__(self):
        super().__init__()
        self._text = "Commands: \"!music\" to get suggestion \n\""\
            "!queue <song/artist> to add to my current queue\" \n"\
            "\"good bot\" to show some love"


class QueueMessage(Message):
    def __init__(self, is_playing):
        super().__init__()
        if not is_playing:
            self._text = "Efe isn't listening to music right now! "\
                "Try again later"
        else:
            self._text = "Adding {} by {} to Efe's current queue. \n{}"


class AprrMessage(Message):
    def __init__(self):
        super().__init__()
        self._text = u"\U0001F49B" + u"\U0001F425"
