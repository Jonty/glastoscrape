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

API_KEY = os.environ["LASTFM_API_KEY"]
YEAR = os.environ["YEAR"]

def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    return s

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


with open('glastonbury_%s_schedule_filtered.csv' % YEAR, 'rb') as fp:
    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        title = row[0]
        if title == "title":
            continue

        print("Fetching %s" % title)
        get_info(title)
        get_similar(title)
