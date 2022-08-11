#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 14:36:35 2022

@author: efearikan
"""

import tweetify
import pickle


def main():
    try:
        with open('dump.pickle', 'rb') as file:
            tfy = tweetify.Tweetify()
            [tfy.last_mention_id, tfy.last_tweet_id] = pickle.load(file)
    except (OSError):
        tfy = tweetify.Tweetify()
    tfy.run()


if __name__ == '__main__':
    main()
