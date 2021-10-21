"""
dblp_survey.py

Author: Jan Zahalka, Czech Technical University in Prague

Given a list of keywords, a list of conferences/journals and a year, selects
all papers from the DBLP database that come from any of the specified
conferences/journals, contain at least one keyword from the list and have been
published between the given year and today.


Required files:
dblp_survey/inputs/keywords.csv: A CSV file, one entry per line
    The list of keywords, case insensitive. The script will look for exact
    matches, so stemming is highly recommended (for example, "evaluat" finds
    "evaluation", "evaluating", "evaluate" etc.)

dblp_survey/inputs/conf_journ.csv: A CSV file, one entry per line
    The list of conferences and journals. The entries need to match exactly the
    entries in the DBLP XML database within the <journal> (journal article) or
    <booktitle> (conference paper) tags.

dblp_survey/dblp.xml
    The DBLP database in XML format as downloaded from the DBLP website.

dblp_survey/dblp.dtd
    The DTD file accompanying the DBLP database, downloadable from the same
    place as the DB.


Arguments:
year : int
    The oldest year from which publications are considered.
"""

import argparse
from datetime import datetime
from lxml import etree
import os
import pandas as pd


KEYWORDS_PATH = "inputs/keywords.csv"
CONF_JOURN_PATH = "inputs/conf_journ.csv"
DB_PATH = "dblp.xml"
OUT_DIR = "outputs"
OUT_NO_SPLIT_PATH = os.path.join(OUT_DIR, "dblp_survey.csv")


argparser = argparse.ArgumentParser()
argparser.add_argument("year", type=int, help="The year from which the oldest "
                       "publications to be considered come.")
argparser.add_argument("--split", choices=["none", "per-venue"],
                       default="per-venue", help="'none' if all matching "
                       "papers should be in one file, 'per-source' if each "
                       "file should correspond to papers from one venue "
                       "(conference/journal)")

args = argparser.parse_args()

if args.year > datetime.now().year:
    print("The year %s has not come yet, so there are no publications."
          % args.year)
    exit()

# Load the inputs: the list of journals/conferences and the keywords
keywords = [kw.lower() for kw in pd.read_csv(KEYWORDS_PATH, header=None)[0]]
conf_journs = list(pd.read_csv(CONF_JOURN_PATH, header=None)[0])

conf_journ_info = dict()
for cj in conf_journs:
    conf_journ_info[cj] = dict()
    conf_journ_info[cj]["filename"] =\
        cj.replace(".", "").replace(" ", "-").lower()
    conf_journ_info[cj]["count"] = 0


year_info = dict()
for year in range(args.year, datetime.now().year + 1):
    year_info[year] = 0

# Ensure the output directory exists
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

i = 0
count = 0

for event, element in etree.iterparse(DB_PATH, dtd_validation=True,
                                      tag=["article", "inproceedings"]):
    if element.tag == "article":
        xpath = "./journal"
    elif element.tag == "inproceedings":
        xpath = "./booktitle"

    try:
        conf_journ = element.xpath(xpath)[0].text
    except IndexError:
        # This means there is no information parsed, continue
        continue

    year = int(element.xpath("./year")[0].text)
    title = element.xpath("./title")[0].text

    if not title:
        title = etree.tostring(element.xpath("./title")[0]).decode("utf-8")

    title_lowercase = title.lower()

    if year >= args.year and conf_journ in conf_journs:
        for kw in keywords:
            if kw in title_lowercase:
                try:
                    link = element.xpath("./ee")[0].text
                except IndexError:
                    link = ""

                paper_entry = ('%s;%s;%s;=HYPERLINK("%s")\n'
                               % (title, conf_journ, year, link))

                if args.split == "none":
                    out_path = OUT_NO_SPLIT_PATH
                else:
                    out_filename =\
                        "%s.csv" % conf_journ_info[conf_journ]["filename"]
                    out_path = os.path.join(OUT_DIR, out_filename)

                with open(out_path, "a") as f:
                    f.write(paper_entry)

                conf_journ_info[conf_journ]["count"] += 1
                try:
                    year_info[year] += 1
                except KeyError:
                    year_info[year] = 0
                    year_info[year] += 1

                count += 1
                break
    i += 1

    if i % 1000 == 0:
        print("[%s] %s papers processed, %s survey candidates found."
              % (datetime.now(), i, count))

    element.clear()

print("[%s] +++ DBLP SURVEY COMPLETE +++" % datetime.now())
print("[%s] %s papers processed, %s survey candidates found."
      % (datetime.now(), i, count))
print("")
print("STATS BY CONFERENCE/JOURNAL:")
for cj in conf_journ_info:
    print("%s: %s papers" % (cj, conf_journ_info[cj]["count"]))
print("")
print("STATS BY YEAR:")
for year in year_info:
    print("%s: %s papers" % (year, year_info[year]))
