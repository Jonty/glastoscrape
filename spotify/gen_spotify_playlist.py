#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import requests
import re
import time
import json
import urllib
import codecs
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util


playlist_title = "Glastonbury 2022 Artists Top Tracks"
spotify_username = "jontywareing"

token = util.prompt_for_user_token("jontywareing", ["playlist-modify-public", "playlist-read-private", "playlist-modify-private"], redirect_uri='http://localhost:9011') 
spotify = spotipy.Spotify(auth=token)

playlist = spotify.user_playlist_create("jontywareing", name=playlist_title)

def check_artist(name, row):
    results = spotify.search(q='artist:' + name, type='artist')
    if results["artists"]["items"]:
        found = results["artists"]["items"][0]
        if name.lower() == found["name"].lower():
            tracks = spotify.artist_top_tracks(found["uri"])
            for track in tracks["tracks"][:1]: # Top ....one. Two is too many.
                print("Adding '%s' by '%s': %s" % (track["name"], found["name"], track["uri"]))
                spotify.user_playlist_add_tracks(spotify_username, playlist["id"], [track["id"]])
            return True
    return False

filtered = []
artists = set()

with open('../last_fm/glastonbury_2022_schedule_onlymusic.csv', 'r') as fp:
    f = csv.reader(fp, delimiter=',')

    for row in f:
        artist, url, stage, _, _ = row

        if artist == 'title':
            continue

        if artist == 'TBA' or artist == 'TO BE ANNOUNCED' or 'TBC' in artist:
            continue

        if 'SPECIAL GUEST' in artist:
            continue

        if 'COMPERE' in artist:
            continue

        if 'OPEN MIC' in artist:
            continue

        if artist == 'TBA':
            continue

        if '(DJ)' in artist or 'DJ SET' in artist:
            continue

        artist = re.sub('\s\(.*?\)?$', '', artist)
        artist = re.sub('\s-$', '', artist)
        artist = re.sub('\s- LIVE$', '', artist)
        artist = re.sub('\s+', ' ', artist)
        artist = re.sub('[\r\n]', '', artist)

        # Takes care of "Session presents: "
        artist = re.sub('^.*?: ', '', artist)
        artist = artist.strip()

        candidates = [artist]

        # If you want to ignore all the DJ's comment this block out
#       worked = True
#       while worked == True:
#           worked = False

#           for candidate in candidates:
#               for splitter in (
#                       ' VS ', ' B2B ', ' PRESENTS ', ' FT ', 
#                       ' FT. ', 'FEAT', ' AND ', ' & ', ' + ', ',', ' BAND', ' X ', ' -'):

#                   if splitter in candidate:
#                       performers = candidate.split(splitter)
#                       for performer in performers:
#                           performer = re.sub('\s\(.*?\)?$', '', performer)
#                           performer = re.sub('\s-$', '', performer)
#                           performer = re.sub('\s- LIVE$', '', performer)
#                           performer = performer.strip()
#                           if performer not in candidates:
#                               candidates += [performer]
#                               worked = True
        
        if artist in artists:
            continue
        artists.add(artist)

        if not check_artist(artist, row):
            for candidate in candidates:
                if candidate in artists:
                    continue
                artists.add(candidate)
                check_artist(candidate, row)

        time.sleep(0.2)
