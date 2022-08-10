#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 14:36:35 2022

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


class Tweetify():
    def __init__(self):
        # Spotipy initialization
        self.scope = "playlist-read-private, user-library-read, user-read-currently-playing, user-read-playback-state,user-modify-playback-state"
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

        self.tracks = []
        seed(None)

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
            track = Track(artist, name, url,
                          playlist, playlist_link)
            self.tracks.append(track)

    def get_random_track(self):
        self.get_user_playlists()
        self.get_tracks()
        return choice(self.tracks)

    def tweet_it(self):
        track = self.get_random_track()
        self.client.create_tweet(
            text=track.name + " by " + track.artist + '\n'
            "Playlist: " + track.from_playlist + '\n'
            "Playlist Link: " + track.from_playlist_link + "\n" +
            track.url
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
                    self.client.create_tweet(
                        text=u"\U0001F49B" + u"\U0001F425", in_reply_to_tweet_id=(mention_id)
                    )
                else:
                    self.help_tweet(mention_id)
                self.last_mention_id = mentions.meta["newest_id"]
            with open('filename.pickle', 'wb') as file:
                pickle.dump(self.last_mention_id, file)
        else:
            print("Sleeping")

    def suggest_music(self, mention_id):
        track = self.get_random_track()
        self.client.create_tweet(
            text=track.name + " by " + track.artist + '\n'
            "Playlist: " + track.from_playlist + '\n'
            "Playlist Link: " + track.from_playlist_link + "\n" +
            track.url, in_reply_to_tweet_id=(mention_id)
        )

    def help_tweet(self, mention_id):
        self.client.create_tweet(
            text="Mention me with \"!music\" to get a suggestion",
            in_reply_to_tweet_id=(mention_id)
        )

    def add_to_queue(self, mention_id, mention):
        if (self.sp.current_user_playing_track() is not None):
            res = self.sp.search(mention)
            res = res["tracks"]["items"][0]
            artist = res["artists"][0]
            song = res["name"]
            url = res["external_urls"]["spotify"]
            track = Track(artist, song, url)
            self.client.create_tweet(
                text="Adding " + track.name + " by " + track.artist +
                " to Efe's current queue. \n" +
                track.url, in_reply_to_tweet_id=(mention_id)
            )
            self.sp.add_to_queue(url)
        else:
            self.client.create_tweet(
                text="Efe isn't listening to music right now! Try again later",
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


if __name__ == '__main__':
    try:
        with open('filename.pickle', 'rb') as file:
            tfy = Tweetify()
            tfy.last_mention_id = pickle.load(file)
    except (OSError):
        tfy = Tweetify()
    schedule.every(60).seconds.do(tfy.refresh_spotify)
    schedule.every(60).seconds.do(tfy.respond_to_mention)
    print("Starting the bot")
    while (True):
        try:
            schedule.run_pending()
            time.sleep(1)
        except:
            pass
