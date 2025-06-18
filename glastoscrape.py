#!/usr/bin/env python
from lxml import html
import csv
import requests
import os
import re
import datetime

year = os.environ["YEAR"]

response = requests.get(
    f"https://www.glastonburyfestivals.co.uk/line-up/line-up-{year}/?view=stages"
)
root = html.document_fromstring(response.content)

dates_string = root.xpath('.//h2[@class="festival-dates"]/text()')[0]
matches = re.search(
    "(\d+)(?:th|nd) - (\d+)(?:th|nd) ([A-Za-z]+) (\d\d\d\d)", dates_string
)
start_day, end_day, month, year = matches.groups()

DAY_MAP = {}
for day_num in range(int(start_day), int(end_day) + 1):
    dt = datetime.datetime.strptime(f"{day_num} {month} {year} +01:00", "%d %B %Y %z")
    DAY_MAP[dt.strftime("%A").upper()] = dt

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

            timestamp_start_str = timestamp_end_str = ""
            if time:
                start, end = time.split("-")
                start_hr, start_m = start.split(":")
                start_hr, start_m = int(start_hr.strip()), int(start_m.strip())
                end_hr, end_m = end.split(":")
                end_hr, end_m = int(end_hr.strip()), int(end_m.strip())

                timestamp_start = DAY_MAP[day].replace(hour=start_hr, minute=start_m)
                timestamp_end = DAY_MAP[day].replace(hour=end_hr, minute=end_m)

                # If things start or end after after midnight and before 7am, they're the next day
                if start_hr < 7:
                    timestamp_start = timestamp_start + datetime.timedelta(days=1)
                if end_hr < 7:
                    timestamp_end = timestamp_end + datetime.timedelta(days=1)

                timestamp_start_str = timestamp_start.isoformat()
                timestamp_end_str = timestamp_end.isoformat()

            data.append(
                [
                    title,
                    link,
                    stage_name,
                    day,
                    time,
                    description,
                    timestamp_start_str,
                    timestamp_end_str,
                ]
            )

# Sort by name, day, time
data = sorted(data, key=lambda x: (x[0], x[3], x[4]))

with open("glastonbury_%s_schedule.csv" % year, "w") as fp:
    out = csv.writer(fp, delimiter=",")
    out.writerow(
        [
            "title",
            "url",
            "stage",
            "day",
            "time",
            "description",
            "timestamp_start",
            "timestamp_end",
        ]
    )
    out.writerows(data)
