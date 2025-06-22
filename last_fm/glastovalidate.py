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

filtered = [['title', 'url', 'stage', 'day', 'time', 'description', 'start_time', 'end_time', 'mbid', 'lfm_url', 'candidate_name', 'orig_name']]

def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise Exception("Could not derive file name from '%s'" % name)
    return s

def check_exists(candidate, row):
    if not candidate.strip():
        return False

    while True:
        data = None

        try:
            f = 'search_cache/' + get_valid_filename(candidate) + '.json'
        except Exception as e:
            print("Skipping %s due to weird name: %s" % (candidate, e))
            return False

        if os.path.exists(f):
            data = json.load(open(f, 'r'))

        if not data:
            response = requests.get(
                'http://ws.audioscrobbler.com/2.0/?method=artist.search&artist=%s&api_key=%s&format=json' % (urllib.parse.quote(candidate), API_KEY)
            )
            data = json.loads(response.content)

            if response.status_code == 200:
                json.dump(data, open(f, 'w'))

            time.sleep(0.2)

        try:
            matches = data['results']['artistmatches']['artist']

            if matches:
                for match in matches:
                    if match['name'].lower().strip() == candidate.lower().strip():
                        mbid = match['mbid']
                        lfm_name = match['name']
                        lfm_url = match['url']
                        lfm_row = row + [mbid] + [lfm_url] + [candidate] + [row[0]]
                        lfm_row[0] = lfm_name
                        filtered.append(lfm_row)
                        print('YES: ' + lfm_name)
                        return True

            print('NO: ' + candidate)
            return False
        except KeyError as e:
            print('ERROR querying %s (%s), RETRYING. [%s]' % (candidate, e, response.content))
            time.sleep(30)
            continue


valid_stages = []
with codecs.open('valid_stages.txt', 'r', 'utf-8') as fp:
    for stage in fp.read().splitlines():
        if stage.startswith("#"):
            continue
        valid_stages.append(stage)

with open('../glastonbury_%s_schedule.csv' % YEAR, 'rb') as fp:
    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        artist, url, stage, _, _, _, _, _ = row

        if artist == 'title':
            continue

        if stage not in valid_stages:
            print("Skipping '%s' as stage '%s' is not whitelisted" % (artist, stage))
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

        artist = re.sub('\s\(.*?\)?$', '', artist)
        artist = re.sub('\s-$', '', artist)
        artist = re.sub('\s- LIVE$', '', artist)
        artist = re.sub(' DJ SET$', '', artist)
        artist = re.sub('\s+', ' ', artist)
        artist = re.sub('[\r\n]', '', artist)
        
        # Handles [DIALLED IN TAKEOVER] etc
        if not artist.startswith("[") and artist.endswith("]"):
            artist = re.sub('\[.*?\]', '', artist)

        # Takes care of "Session presents: "
        artist = re.sub('^.*?: ', '', artist)
        artist = artist.strip()

        bad_artists = ["arcadia", "pixels", "love"]
        if artist.lower() in bad_artists:
            continue

        candidates = [artist]
        worked = True
        while worked == True:
            worked = False

            for candidate in candidates:
                for splitter in (
                        ' VS ', ' B2B ', ' PRESENTS ', ' PRESENTS: ', ' PRES ', ' FT ', ' WITH ',
                        ' FT. ', 'FEAT', ' AND ', ' & ', ' + ', ',', ' BAND', ' X ', ' -', ' PERFORMED BY ', ' TAKEOVER:', ' W/ ', ' HOSTED BY '):

                    if splitter in candidate:
                        performers = candidate.split(splitter)
                        for performer in performers:
                            performer = re.sub('\s\(.*?\)?$', '', performer)
                            performer = re.sub('\s-$', '', performer)
                            performer = re.sub('\s- LIVE$', '', performer)
                            performer = performer.strip()
                            if performer not in candidates:
                                # Skip "and friends" etc
                                if performer.lower() in ["friends", "guests"] + bad_artists:
                                    continue
                                candidates += [performer]
                                worked = True
        
        if not check_exists(artist, row):
            for candidate in candidates:
                check_exists(candidate, row)


with open('glastonbury_%s_schedule_filtered.csv' % YEAR, 'wb') as fp:
    out = unicodecsv.writer(fp, delimiter=',', encoding='utf-8')
    out.writerows(filtered)



