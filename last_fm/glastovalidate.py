#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodecsv
import requests
import re
import time
import json
import urllib
import codecs
import os

API_KEY = os.environ["LASTFM_API_KEY"]

artists = set()
filtered = [['title', 'url', 'stage', 'day', 'time', 'mbid', 'lfm_url', 'orig_name']]

def check_exists(candidate, row):
    if not candidate.strip():
        return False

    while True:
        response = requests.get(
            'http://ws.audioscrobbler.com/2.0/?method=artist.search&artist=%s&api_key=%s&format=json' % (urllib.quote(candidate.encode('utf8')), API_KEY)
        )
        data = json.loads(response.content)

        try:
            matches = data['results']['artistmatches']['artist']
            if matches:
                for match in matches:
                    if match['name'].lower().strip() == candidate.lower().strip():
                        mbid = match['mbid']
                        lfm_name = match['name']
                        lfm_url = match['url']
                        lfm_row = row + [mbid] + [lfm_url] + [candidate]
                        lfm_row[0] = lfm_name
                        filtered.append(lfm_row)
                        print 'YES: ' + lfm_name
                        return True

            print 'NO: ' + candidate
            return False
        except KeyError, e:
            print 'ERROR querying %s (%s), RETRYING. [%s]' % (candidate, e, response.content)
            time.sleep(30)
            continue


with codecs.open('valid_stages.txt', 'r', 'utf-8') as fp:
    valid_stages = fp.read().splitlines()

with open('../glastonbury_2017_schedule.csv', 'r') as fp:
    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        artist, url, stage, _, _ = row

        if artist == 'title':
            continue

        if stage not in valid_stages:
            print "Skipping '%s' as stage '%s' is not whitelisted" % (artist, stage)
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
        worked = True
        while worked == True:
            worked = False

            for candidate in candidates:
                for splitter in (
                        ' VS ', ' B2B ', ' PRESENTS ', ' FT ', 
                        ' FT. ', 'FEAT', ' AND ', ' & ', ' + ', ',', ' BAND', ' X '):

                    if splitter in candidate:
                        performers = candidate.split(splitter)
                        for performer in performers:
                            performer = re.sub('\s\(.*?\)?$', '', performer)
                            performer = re.sub('\s-$', '', performer)
                            performer = re.sub('\s- LIVE$', '', performer)
                            performer = performer.strip()
                            if performer not in candidates:
                                candidates += [performer]
                                worked = True
        
        if artist in artists:
            continue
        artists.add(artist)

        if not check_exists(artist, row):
            for candidate in candidates:
                if candidate in artists:
                    continue
                artists.add(candidate)
                check_exists(candidate, row)

        time.sleep(0.2)


with open('glastonbury_2017_schedule_filtered.csv', 'w') as fp:
    out = unicodecsv.writer(fp, delimiter=',', encoding='utf-8')
    out.writerows(filtered)



