import csv
import os

unique_keys = set()

origin_file = os.path.join(os.getcwd(), "datasets", "hanzi_prepared.csv")
update_file = os.path.join(os.getcwd(), "datasets", "hanzi_nokey.csv")

merged_file = os.path.join(os.getcwd(), "datasets", "hanzi_hsk_complete_set.csv")

origin_lines = []

with open(origin_file) as origin_descriptor:
    for line in origin_descriptor:
        line = line.replace('\n', '')
        line_no, key, *rest = line.split(',')
        unique_keys.add(key)
        origin_lines.append(line.split(','))

update_lines = []
with open(update_file) as update_descriptor:
    for line in update_descriptor:
        line = line.replace('\n', '')
        line_no, key, *rest = line.split(',')
        if key not in unique_keys:
            update_lines.append(line.split(',')[1:])

LAST_NO = 456 

for I in range(0, len(update_lines), 5):
    for i in range(5):
        print(update_lines[I+i])
        origin_lines.append([str(LAST_NO+(I//5)+1)] + update_lines[I+i])

with open(merged_file, "w") as updated_descriptor:
    writer = csv.writer(updated_descriptor)
    writer.writerows(origin_lines)
