#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import html
import csv
import requests
import os

YEAR = os.environ["YEAR"]

response = requests.get("https://www.glastonburyfestivals.co.uk/line-up/line-up-%s/" % YEAR)
root = html.document_fromstring(response.content)

with open('valid_stages.txt', 'w') as vs:
    area_nodes = root.xpath('//div[@class=\"nav_box\"]')
    for node in area_nodes:
        for stage in node.getchildren():
            if stage.tag == "h2":
                vs.write("## " + stage.text.strip() + "\n")
            if stage.tag == "a":
                vs.write(stage.text.strip() + "\n")
