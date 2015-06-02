#!/usr/bin/env python
import lxml.html
import unicodecsv

site = 'http://www.glastonburyfestivals.co.uk/line-up/line-up-2015/?artist'
root = lxml.html.parse(site).getroot()

artist_nodes = root.xpath('//*[@id=\"main\"]/div[2]/div/ul/li')

data = [['title', 'url', 'stage', 'day', 'time']]

for node in artist_nodes:
    title, stage, day, time = node.getchildren()
    link = None
    children = title.getchildren()
    if children:
        link = children[0].attrib['href']
        title = children[0]

    data.append([title.text, link, stage.text, day.text, time.text])

with open('glastonbury_2015_schedule.csv', 'w') as fp:
    out = unicodecsv.writer(fp, delimiter=',', encoding='utf-8')
    out.writerows(data)
