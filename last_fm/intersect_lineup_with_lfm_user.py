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
import string
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
    return data

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
    return data

def get_user_top_artists(user, period="overall", limit=0):
    response = requests.get(
        'https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&format=json&limit=1000&period=%s' % (urllib.parse.quote(user), API_KEY, period)
    )
    data = json.loads(response.content)

    return {item["name"]: int(item["playcount"]) for item in data["topartists"]["artist"] if int(item["playcount"]) >= limit}

recommended = defaultdict(list)
counts = defaultdict(int)
instances = defaultdict(set)

with open('glastonbury_%s_schedule_filtered.csv' % YEAR, 'rb') as fp:
    top_artists = get_user_top_artists(LFM_USER, limit=20)
    top_artists_recent = get_user_top_artists(LFM_USER, period="12month", limit=4)

    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        title = row[0]
        if title == "title":
            continue

        similar_data = get_similar(title)["similarartists"]
        resolved_artist = similar_data["@attr"]["artist"]

        if not resolved_artist in counts:
            if resolved_artist in top_artists_recent:
                counts[resolved_artist] += 50
            elif resolved_artist in top_artists:
                counts[resolved_artist] += 10

        for item in similar_data["artist"]:
            similar_artist = item["name"]

            if similar_artist in top_artists:
                if similar_artist not in recommended[resolved_artist]:
                    amount = 1
                    if similar_artist in top_artists_recent:
                        amount = 3

                    counts[resolved_artist] += amount
                    recommended[resolved_artist].append(similar_artist)

        instances[resolved_artist].add(tuple(row))

print("""
<head>
    <meta charset="UTF-8">
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
            margin: 30px;
            border-top: 4px dashed black;
        }
    </style>
    <script type="text/javascript">
    function filter() {
        var day = window.location.hash.substring(1);
        if (day == "") {
            day = "all";
        }

        [...document.getElementsByClassName("artist")].forEach(
            (element, index, array) => {
                if (element.className.includes(day)) {
                    element.style.display = "block";
                } else {
                    element.style.display = "none";
                }
            }
        );

        [...document.getElementsByClassName("filter")].forEach(
            (element, index, array) => {
                if (element.className.includes(day)) {
                    element.style.fontWeight = "bold";
                } else {
                    element.style.fontWeight = "";
                }
            }
        );
        
    }
    </script>
</head>
<body onhashchange="filter()" onload="filter()">
""" % (YEAR, LFM_USER))
print("<h1>Glastonbury %s: %s</h1>" % (YEAR, LFM_USER))
print("""
    Filter: 
    <a href="#all" class="filter all">All</a> | 
    <a href="#wednesday" class="filter wednesday">Wed</a> | 
    <a href="#thursday" class="filter thursday">Thu</a> | 
    <a href="#friday" class="filter friday">Fri</a> | 
    <a href="#saturday" class="filter saturday">Sat</a> | 
    <a href="#sunday" class="filter sunday">Sun</a>
""") 
print("<br>")

for k, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
    info = get_info(k)
    name = info["artist"]["name"]

    days = defaultdict(list)
    websites = set()
    for instance in instances[k]:
        days[instance[3]].append(instance)
        if instance[1]:
            websites.add(instance[1].strip().rstrip("/"))

    print("<div class=\"artist all %s\">" % " ".join([v.lower() for v in days.keys()]))
    website = ""
    if instance[1] and len(websites) == 1:
        website = " <a href='%s' target='_blank'>🌐</a>" % instance[1]

    print("<h2>%s%s</h2>" % (name, website))
    print("<!--%s: %s / %s-->" % (name, count, len(recommended[k])))
    print("<h4 style=\"margin-left: 20px\"><i>%s</i></h4>" % ", ".join(t["name"] for t in info["artist"]["tags"]["tag"] if t["name"] != "seen live"))
    if info["artist"]["bio"]["summary"][0] != " ":
        print("<p style=\"margin-left: 20px\"><i><small>%s</small></i></p>" % info["artist"]["bio"]["summary"])

    print("<ul>")

    for day in ["WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]:
        for instance in sorted(days[day], key=lambda x: x[4]):
            orig_name = instance[9]

            website = ""
            if instance[1] and len(websites) > 1:
                website = " <a href='%s' target='_blank'>🌐</a>" % instance[1]

            print("<li>%s, %s from %s%s</li>" % (instance[3].capitalize(), string.capwords(instance[2]), instance[4], website))

            if orig_name.lower().strip() != name.lower().strip():
                print("<p style=\"margin-top: 5px; margin-bottom: 5px;\"><small>%s</small></p>" % orig_name)
            if instance[5]:
                print("<p style=\"margin-top: 5px; margin-bottom: 5px;\"><i><small>\"%s\"</i></small></p>" % instance[5])

    print("</ul>")
    
    lastfm_library_url = "https://www.last.fm/user/%s/library/music/%s" % (LFM_USER, urllib.parse.quote_plus(name))
    if name in top_artists_recent:
        listened = "You've <a href='%s?date_preset=LAST_365_DAYS' target='_blank'>listened</a> to them this year. " % lastfm_library_url
    elif name in top_artists:
        listened = "You've <a href='%s' target='_blank'>listened</a> to them. " % lastfm_library_url
    else:
        listened = ""

    print("<p style=\"margin-left: 20px\"><small><strong>%sSimilar artists you've listened to (%s):</strong> %s</small></p>" % (listened, len(recommended[k]), ", ".join(list(recommended[k])[:20])))
    print("<hr>")
    print("</div>")
    print("</body>")
