import csv
import os

lines = []
with open("trading_affirmations.csv") as origin_file:
    reader = csv.reader(origin_file)
    for line in reader:
        lines.append(line)

out_lines = []
line = lines.pop(0)

while lines:
    if len(line) < 300:
        line += lines.pop(0)

    if len(line)>=300:
        out_lines.append(line)
        line = ""

print(out_lines[-3])
print(out_lines[-2])
print(out_lines[-1])

