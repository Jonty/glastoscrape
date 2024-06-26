#!/usr/bin/env python
from lxml import html
import csv
import requests
import os

year = os.environ['YEAR']

response = requests.get('https://www.glastonburyfestivals.co.uk/line-up/line-up-%s/?artist' % year)
root = html.document_fromstring(response.content)

artist_nodes = root.xpath('//*[@id=\"main\"]/div[2]/div/ul/li')

data = [['title', 'url', 'stage', 'day', 'time', 'description']]

for node in artist_nodes:
    title, stage, day, time = node.getchildren()
    link = None
    description = None

    if 'title' in title.attrib:
        description = title.attrib['title'].strip()

    children = title.getchildren()
    if children:
        link = children[0].attrib['href'].strip()
        title = children[0]

    if title.text:
        title = title.text.strip()
        stage = stage.text.strip()
        if day.text:
            day = day.text.strip()
        else:
            day = None
        if time.text:
            time = time.text.strip()
        else:
            time = None
        data.append([title, link, stage, day, time, description])

with open('glastonbury_%s_schedule.csv' % year, 'w') as fp:
    out = csv.writer(fp, delimiter=',')
    out.writerows(data)
