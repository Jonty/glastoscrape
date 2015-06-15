#!/usr/bin/env python
import unicodecsv
import requests
import re
import time
import json
import urllib

artists = set()
filtered = [['title', 'url', 'stage', 'day', 'time', 'lfm_id']]

with open('glastonbury_2015_schedule.csv', 'r') as fp:
    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        artist, url, stage, _, _ = row

        if artist == 'title':
            continue

        if 'CIRCUS' in stage or 'KIDZ' in stage or 'MOVIE' in stage or 'CINEMA' in stage:
            continue

        if artist == 'TBA' or artist == 'TO BE ANNOUNCED' or 'TBC' in artist:
            continue

        if 'DJS' in artist or 'DJ\'S' in artist:
            continue

        if 'SPECIAL GUEST' in artist:
            continue

        if 'COMPERE' in artist:
            continue

        if 'OPEN MIC' in artist:
            continue

        if '(DJ)' in artist or 'DJ SET' in artist:
            continue
        
        artist = re.sub('\s\(.*?\)?$', '', artist)
        artist = re.sub('\s-$', '', artist)
        artist = re.sub('\s\s+', '', artist)
        artist = artist.strip()

        if artist in artists:
            continue
        artists.add(artist)

        response = requests.get('http://www.last.fm/ajax/verifyResourceByName?type=6&name=' + urllib.quote(artist.encode('utf8')))
        data = json.loads(response.content)

        if data.get('resource', False):
            lfm_id = data['resource']['id']
            lfm_name = data['resource']['name']
            lfm_row = row + [lfm_id]
            lfm_row[0] = lfm_name
            filtered.append(lfm_row)
            print 'YES: ' + lfm_name
        else:
            print 'NO: ' + artist

        time.sleep(0.2)


with open('glastonbury_2015_schedule_filtered.csv', 'w') as fp:
    out = unicodecsv.writer(fp, delimiter=',', encoding='utf-8')
    out.writerows(filtered)
