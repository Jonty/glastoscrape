#!/usr/bin/env python
import lxml.html
import unicodecsv

site = 'http://www.glastonburyfestivals.co.uk/line-up/line-up-2017/?artist'
root = lxml.html.parse(site).getroot()

artist_nodes = root.xpath('//*[@id=\"main\"]/div[2]/div/ul/li')

data = [['title', 'url', 'stage', 'day', 'time']]

for node in artist_nodes:
    title, stage, day, time = node.getchildren()
    link = None
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
        data.append([title, link, stage, day, time])

with open('glastonbury_2017_schedule.csv', 'w') as fp:
    out = unicodecsv.writer(fp, delimiter=',', encoding='utf-8')
    out.writerows(data)
