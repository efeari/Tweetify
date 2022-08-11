#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 18:35:17 2022

@author: efearikan
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from random import choice, seed
import tweepy
import os
import time
import pickle
import schedule
import message
import track as tr


class Tweetify():
    def __init__(self):
        # Spotipy initialization
        self.scope = "playlist-read-private, user-library-read, \
            user-read-currently-playing, user-read-playback-state, \
            user-modify-playback-state"
        self.init_spotipy()

        # Tweepy initialization
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")
        access_token = os.environ.get("ACCESS_TOKEN")
        access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
        self.client = tweepy.Client(
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        self.twitter_id = self.client.get_me()[0]["id"]
        self.last_mention_id = 1
        self.last_tweet_id = 1

        self.tracks = []
        seed(None)

        schedule.every(60).seconds.do(self.refresh_spotify)
        schedule.every(60).seconds.do(self.respond_to_mention)
        schedule.every().day.at("10:00").do(self.suggest_music)

    def init_spotipy(self):
        self.auth_manager = SpotifyOAuth(
            scope=self.scope)
        self.token = self.auth_manager.get_cached_token()
        self.sp = spotipy.Spotify(
            auth=self.token['access_token'], requests_timeout=10, retries=10)
        self.user_id = self.sp.me()['id']

    def refresh_spotify(self):
        if self.auth_manager.is_token_expired(self.token):
            print("Acces token expired. Refreshing...")
            self.token = self.auth_manager.get_cached_token()
            self.sp = spotipy.Spotify(auth=self.token['access_token'])
        else:
            print("Access token lookin good")

    def run(self):
        print("Starting the bot")
        while (True):
            try:
                schedule.run_pending()
                time.sleep(1)
            except:
                pass

    def get_user_playlists(self):
        playlists = self.sp.current_user_playlists()
        self.playlists = []
        for playlist in playlists['items']:
            if playlist['owner']['id'] != self.user_id:
                continue
            else:
                self.playlists.append(playlist)
        # for item in self.sp.current_user_saved_tracks()['items']:
        #     track = item['track']
        #     artist = track['artists'][0]
        #     name = track['name']
        #     url = track["external_urls"]["spotify"]
        #     # img_url = track['album']['images'][0]['url']
        #     track = Track(artist, name, url, "Liked Songs", "-")
        #     self.tracks.append(track)

    def get_tracks(self):
        for playlist in self.playlists:
            results = self.sp.playlist(playlist['id'], fields="tracks,next")
            tracks = results['tracks']
            self.iterate_tracks(
                tracks, playlist["name"], playlist["external_urls"])
            while tracks['next']:
                tracks = self.sp.next(tracks)
                self.iterate_tracks(
                    tracks, playlist["name"], playlist["external_urls"])

    def iterate_tracks(self, results, playlist, playlist_link):
        for i, item in enumerate(results['items']):
            track = item['track']
            if track["is_local"]:
                continue
            artist = track['artists'][0]
            name = track['name']
            url = track["external_urls"]["spotify"]
            # img_url = track['album']['images'][0]['url']
            track = tr.Track(artist, name, url,
                             playlist, playlist_link)
            self.tracks.append(track)

    def get_random_track(self):
        self.get_user_playlists()
        self.get_tracks()
        return choice(self.tracks)

    def basic_tweet(self, msg, mention_id=None):
        self.client.create_tweet(
            text=msg, in_reply_to_tweet_id=(mention_id)
        )

    def respond_to_mention(self):
        mentions = self.client.get_users_mentions(
            self.twitter_id, user_auth=True, since_id=self.last_mention_id,
            expansions='author_id')

        # Loop
        if mentions[0] is not None:
            for user in mentions[1]["users"]:
                self.is_following(user)
            for mention in mentions[0]:
                mention_id = mention.id
                # Like the tweet first!
                self.client.like(mention_id, user_auth=True)
                mention = str(mention)
                print("Responding to message")
                if "!music" in mention:
                    self.suggest_music(mention_id)
                elif "!queue" in mention:
                    mention = mention.replace(
                        "@Tweetify_Bot", '').replace("!queue", '')
                    self.add_to_queue(mention_id, mention)
                elif "good bot" in mention or "Good bot" in mention:
                    msg = message.AprrMessage().get
                    self.basic_tweet(msg, mention_id)
                else:
                    msg = message.HelpMessage().get
                    self.basic_tweet(msg, mention_id)

            self.last_mention_id = mentions.meta["newest_id"]
            with open('dump.pickle', 'wb') as file:
                pickle.dump([self.last_mention_id, self.last_tweet_id], file)
        else:
            print("Sleeping")

    def suggest_music(self, mention_id=None):
        track = self.get_random_track()
        msg = message.SuggestionMessage()
        msg.format_text(track.name, track.artist,
                        track.from_playlist,
                        track.from_playlist_link,
                        track.url)
        tweet = self.client.create_tweet(
            text=msg.get, in_reply_to_tweet_id=(mention_id)
        )
        tweet.data['id']

    def help_tweet(self, mention_id):
        msg = message.HelpMessage()
        self.client.create_tweet(
            text=msg.get,
            in_reply_to_tweet_id=(mention_id)
        )

    def add_to_queue(self, mention_id, mention):
        if (self.sp.current_user_playing_track() is not None):
            res = self.sp.search(mention)
            res = res["tracks"]["items"][0]
            artist = res["artists"][0]
            song = res["name"]
            url = res["external_urls"]["spotify"]
            track = tr.Track(artist, song, url)
            msg = message.QueueMessage(True)
            msg.format_text(track.name, track.artist, track.url)
            self.client.create_tweet(
                text=msg.get, in_reply_to_tweet_id=(mention_id)
            )
            self.sp.add_to_queue(url)
        else:
            msg = message.QueueMessage(False).get
            self.client.create_tweet(
                text=msg,
                in_reply_to_tweet_id=(mention_id)
            )

    def follow_followers(self):
        followers = self.client.get_users_followers(
            self.twitter_id, user_auth=True)
        for follower in followers[0]:
            self.client.follow_user(follower.id, user_auth=True)

    def is_following(self, username):
        followings = self.client.get_users_following(
            self.twitter_id, user_auth=True)
        if username not in [following.username for following in followings[0]]:
            _id = self.client.get_user(username=username, user_auth=True)[0].id
            self.client.follow_user(_id, user_auth=True)
