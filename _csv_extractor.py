import os
import csv
import re
import random
from copy import deepcopy

def split_definition(definition):
    parts = re.split("[,;]",definition)
    parts = list(filter( lambda _ : len(_) < 13, parts))
    parts.sort(key = lambda _ : len(_))
    for i, _ in enumerate(parts):
        parts[i] = _.strip()
    return parts[:5]

def extract_hanzi(hanzifile):
    extracted = []
    unique_pins = {}
    with open(hanzifile) as cn_file:
        reader = csv.DictReader(cn_file, quotechar='"')
        headers = reader.fieldnames
        for line in reader:
            if "definition" not in line:
                continue
            charcter = line["charcter"].strip()
            pin = line["pinyin"].strip()
            stroke_count = line["stroke_count"]
            definition = line["definition"]
            if not stroke_count:
                continue
            if not pin:
                continue

            stroke_count = int(stroke_count.split()[0])

            features = split_definition(definition)
            if not len(features) >= 1:
                continue

            if pin not in unique_pins:
                unique_pins[pin] = (charcter, int(stroke_count), features[0])
            else:
                if unique_pins[pin][1] < int(stroke_count):
                    continue
                else:
                    unique_pins[pin] = (charcter, int(stroke_count), features[0])

    for i, (pin, (charctr, st_count, feat)) in enumerate(unique_pins.items()):
        if pin and feat:
            extracted.append([charctr, pin,"",feat])
        elif pin:
            extracted.append([charctr, pin])


    extracted = sorted(extracted, key = lambda _ : _[1])

    return extracted 

uniquie_pins = extract_hanzi(os.path.join(os.getcwd(), "datasets",  "hanziDB.csv"))

with open(os.path.join(os.getcwd(), "datasets", "hanzi_pins.csv"), "w") as hanzi_prepared:
   csvwriter = csv.writer(hanzi_prepared)
   for i, line in enumerate(uniquie_pins):
       csvwriter.writerow([i//5]+[line[0]]+["",""]+line[1:])
