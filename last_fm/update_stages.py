#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import html
import csv
import requests
import os

YEAR = os.environ["YEAR"]

response = requests.get(
    "https://www.glastonburyfestivals.co.uk/line-up/line-up-%s/?view=stages" % YEAR
)
root = html.document_fromstring(response.content)

with open("valid_stages.txt", "w") as vs:
    area_nodes = root.xpath('//ul[@class="subnav"]//a')
    for node in area_nodes:
        if node.attrib["class"] == "group-link":
            vs.write("## " + node.text_content().strip() + "\n")
        if node.attrib["class"] == "stage-link":
            vs.write(node.text_content().strip() + "\n")
