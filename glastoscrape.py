#!/usr/bin/env python
from lxml import html
import csv
import requests
import os

year = os.environ["YEAR"]

response = requests.get(
    f"https://www.glastonburyfestivals.co.uk/line-up/line-up-{year}/?view=stages"
)
root = html.document_fromstring(response.content)

stage_names = root.xpath('//*[@class="stage-name"]/button/text()')
stage_sections = root.xpath('//div[contains(@class, "stage-container")]')
stage_data = zip(stage_names, stage_sections)

data = []

for stage_name, stage_node in stage_data:
    days = stage_node.xpath('./h4[@class="stage-day"]/text()')
    event_tables = stage_node.xpath("./table")
    event_data = zip(days, event_tables)

    for day, table_node in event_data:
        event_rows = table_node.xpath(".//tr")
        for row in event_rows:
            title = row[0].text_content().strip()
            time = row[1].text_content().strip()
            description = ""
            link = ""

            link_node = row[0].xpath("./a")
            if link_node:
                link = link_node[0].attrib["href"].strip()

                if "title" in link_node[0].attrib:
                    description = link_node[0].attrib["title"].strip()

            data.append([title, link, stage_name, day, time, description])

# Sort by name, day, time
data = sorted(data, key=lambda x: (x[0], x[3], x[4]))

with open("glastonbury_%s_schedule.csv" % year, "w") as fp:
    out = csv.writer(fp, delimiter=",")
    out.writerow(["title", "url", "stage", "day", "time", "description"])
    out.writerows(data)
