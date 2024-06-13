#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodecsv
import requests
import re
import time
import json
import urllib.request, urllib.parse, urllib.error
import codecs
import os
from collections import defaultdict

API_KEY = os.environ["LASTFM_API_KEY"]
LFM_USER = os.environ["LFM_USER"]
YEAR = os.environ["YEAR"]

def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    return s

def get_info(artist):
    f = 'info_data/' + get_valid_filename(artist) + '.json'
    if os.path.exists(f):
        return json.load(open(f, 'r'))

    while True:
        try:
            response = requests.get(
                'http://ws.audioscrobbler.com/2.0/?method=artist.getInfo&artist=%s&api_key=%s&format=json' % (urllib.parse.quote(artist), API_KEY)
            )
            data = json.loads(response.content)
            break

        except KeyError as e:
            print('ERROR querying %s (%s), RETRYING. [%s]' % (candidate, e, response.content))
            time.sleep(30)
            continue

    json.dump(data, open(f, 'w'))
    return json

def get_similar(artist):
    f = 'similar_data/' + get_valid_filename(artist) + '.json'
    if os.path.exists(f):
        return json.load(open(f, 'r'))

    while True:
        try:
            response = requests.get(
                'http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=%s&api_key=%s&format=json' % (urllib.parse.quote(artist), API_KEY)
            )
            data = json.loads(response.content)
            break

        except KeyError as e:
            print('ERROR querying %s (%s), RETRYING. [%s]' % (candidate, e, response.content))
            time.sleep(30)
            continue

    json.dump(data, open(f, 'w'))
    return json

def get_user_top_artists(user):
    response = requests.get(
        'https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&format=json&limit=1000' % (urllib.parse.quote(user), API_KEY)
    )
    data = json.loads(response.content)
    return [item["name"] for item in data["topartists"]["artist"]]

recommended = defaultdict(list)

with open('glastonbury_%s_schedule_filtered.csv' % YEAR, 'rb') as fp:
    top_artists = get_user_top_artists(LFM_USER)

    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        title = row[0]
        if title == "title":
            continue

        for item in get_similar(title)["similarartists"]["artist"]:
            similar_artist = item["name"]

            if similar_artist in top_artists:
                recommended[title].append(similar_artist)

print("""
<head>
    <title>Glastonbury %s recommendations for %s</title>
    <style type=\"text/css\">
        body {
            font-family: Helvetica, Bitstream Vera Sans, sans-serif;
            color: #000000;
        }
        A:link {
            text-decoration: none;
            color: #008000;
        }
        A:visited {
            text-decoration: none;
            color: #008000;
        }
        A:active {
            text-decoration: none;
            color: #008000;
        }
        A:hover {
            text-decoration: underline;
            color: #008000;
        }
        hr {
            margin: 50px;
            border-top: 4px dashed black;
        }
        </style>
</head>""" % (YEAR, LFM_USER))
print("<h1>Glastonbury %s: %s</h1>" % (YEAR, LFM_USER))
print("<br>")

for k in sorted(recommended, key=lambda key: len(recommended[key]), reverse=True):
    info = get_info(k)
    print("<h2>%s</h2>" % info["artist"]["name"])
    print("<h4 style=\"margin-left: 20px\"><i>%s</i></h4>" % ", ".join(t["name"] for t in info["artist"]["tags"]["tag"]))
    print("<p style=\"margin-left: 20px\"><small>%s</small></p>" % info["artist"]["bio"]["summary"])
    print("<p><small><strong>Similar artists you've listened to:</strong> %s</small></p>" % ", ".join(recommended[k][:20]))
    print("<hr>")