#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodecsv
import requests
import re
import time
import codecs

with codecs.open('valid_stages.txt', 'r', 'utf-8') as fp:
    valid_stages = fp.read().splitlines()

filtered = []

with open('../glastonbury_2022_schedule.csv', 'r') as fp:
    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')

    for row in f:
        artist, url, stage, _, _ = row

        if stage not in valid_stages:
            print "Skipping '%s' as stage '%s' is not whitelisted" % (artist, stage)
            continue

        filtered.append(row)

with open('glastonbury_2022_schedule_onlymusic.csv', 'w') as fp:
    out = unicodecsv.writer(fp, delimiter=',', encoding='utf-8')
    out.writerows(filtered)



