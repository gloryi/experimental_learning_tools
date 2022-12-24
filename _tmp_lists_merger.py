import csv
import os

unique_keys = set()

#origin_file = os.path.join(os.getcwd(), "datasets", "hsk_12_prepared.csv")
origin_file = None 
sets_dir = os.path.join(os.getcwd(), "learning_sets")
set_dir = os.path.join(sets_dir, "peg_wiki")

update_file = os.path.join(set_dir, "raw_features.csv")
merged_file = os.path.join(set_dir, "features.csv")
LAST_NO = 0 

origin_lines = []
update_lines = []

if origin_file:
    with open(origin_file) as origin_descriptor:
        for line in origin_descriptor:
            line = line.replace('\n', '')
            line_no, key, *rest = line.split(',')
            unique_keys.add(key)
            origin_lines.append(line.split(','))

if update_file:
    with open(update_file) as update_descriptor:
        for line in update_descriptor:
            line = line.replace('\n', '')
            line_no, key, *rest = line.split(',')
            if key not in unique_keys:
                line_prep = line.split(',')
                update_lines.append(line_prep)


for I in range(0, len(update_lines), 5):
    for i in range(5):
        origin_lines.append([str(LAST_NO+(I//5)+1)] + update_lines[I+i])

with open(merged_file, "w") as updated_descriptor:
    writer = csv.writer(updated_descriptor)
    writer.writerows(origin_lines)
