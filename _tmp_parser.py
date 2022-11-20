import os
import csv
import re

extracted = []

with open(os.path.join(os.getcwd() ,"hanziDB.csv")) as cn_file:
    reader = csv.DictReader(cn_file)
    headers = reader.fieldnames
    for line in reader:
        if "definition" not in line:
            continue
        charcter = line["charcter"]
        pin = line["pinyin"]
        definition = line["definition"]
        if ";" in definition or "," in definition:
            definition = re.split("[;,]+",definition)[0]
        if not definition or "(" in definition or ")" in definition or " " in definition or len(definition)>8:
            continue
        if "hsk_levl" not in line:
            continue
        if not line["hsk_levl"] or int(line["hsk_levl"]) > 7:
            continue

        extracted.append([charcter, definition])

with open(os.path.join(os.getcwd() ,"glyphs_set.csv"), "w") as cn_file:
    writer = csv.writer(cn_file)
    writer.writerows(extracted)

