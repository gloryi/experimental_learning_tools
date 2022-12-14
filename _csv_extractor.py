import os
import csv
import re
import random
from copy import deepcopy

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
            if not stroke_count:
                continue
            if not pin:
                continue

            stroke_count = int(stroke_count.split()[0])

            if pin not in unique_pins:
                unique_pins[pin] = (charcter, int(stroke_count))
            else:
                if unique_pins[pin][1] < int(stroke_count):
                    continue
                else:
                    unique_pins[pin] = (charcter, int(stroke_count))


    for i, (pin, (charctr, st_count)) in enumerate(unique_pins.items()):
        extracted.append([charctr, pin])
        # if "\u0304" in pin:
        #     extracted.append("---")
        # elif ""

    extracted = sorted(extracted, key = lambda _ : _[1])
    extracted = [[i]+_ for i, _ in enumerate(extracted)]

    return extracted 

uniquie_pins = extract_hanzi(os.path.join(os.getcwd(), "datasets",  "hanziDB.csv"))

with open(os.path.join(os.getcwd(), "datasets", "hanzi_pins.csv"), "w") as hanzi_prepared:
   csvwriter = csv.writer(hanzi_prepared)
   for line in uniquie_pins:
       csvwriter.writerow(line)
