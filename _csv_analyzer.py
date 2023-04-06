import csv
import os
import random

# from collections import namedtuple

origin_file = None
sets_dir = os.path.join(os.getcwd(), "learning_sets")
set_dir = os.path.join(sets_dir, "personal_set")
# set_dir = os.path.join(sets_dir, "latvian_set")

analysis_file = os.path.join(set_dir, "features.csv")
report_file = os.path.join(set_dir, "corrections.log")
LAST_NO = 0

analysis_lines = []
report_lines = []

if analysis_file:
    with open(analysis_file) as analysis_descriptor:
        for line in analysis_descriptor:
            line = line.replace("\n", "")
            no, *features = line.split(",")
            analysis_lines.append(features)

overlap_size = 3
for i, ref_line in enumerate(analysis_lines[:-1]):
    for j, test_line in enumerate(analysis_lines[i + 1 :]):
        first_ltrs = set(ref_line[0][:overlap_size])
        secnd_ltrs = set(test_line[0][:overlap_size])
        overlap = first_ltrs.union(secnd_ltrs)
        len_total = len(first_ltrs) + len(secnd_ltrs)
        overlap_len = len(overlap)
        delta = len_total - overlap_len
        if delta >= overlap_size:
            report_lines.append(
                f"OVERLAP {i+1} {j+i+2}" + "\n\t" + f"{ref_line[0]} <==> {test_line[0]}"
            )
report_lines.append("\n")

overlap_size = 1
for i, ref_line in enumerate(analysis_lines[:-1]):
    for w1, w2 in zip(ref_line[:-1], ref_line[1:]):
        first_ltrs = set(w1[:overlap_size])
        secnd_ltrs = set(w2[:overlap_size])
        overlap = first_ltrs.union(secnd_ltrs)
        len_total = len(first_ltrs) + len(secnd_ltrs)
        overlap_len = len(overlap)
        delta = len_total - overlap_len
        if delta >= overlap_size:
            report_lines.append(f"INNER LAP {i+1}" + "\n\t" + f"{w1} <==> {w2}")
report_lines.append("\n")

optimal_word_len_high = 9
for i, ref_line in enumerate(analysis_lines):
    if any(len(_) > optimal_word_len_high for _ in ref_line):
        report_lines.append(
            f"OVERFLOW {i+1} "
            + "\n\t"
            + "//".join(_ for _ in ref_line if len(_) > optimal_word_len_high)
        )
report_lines.append("\n")

optimal_word_len_low = 4
for i, ref_line in enumerate(analysis_lines):
    if any(len(_) < optimal_word_len_low for _ in ref_line):
        report_lines.append(
            f"UNDERFLOW {i+1} "
            + "\n\t"
            + "//".join(_ for _ in ref_line if len(_) < optimal_word_len_low)
        )
report_lines.append("\n")

max_line_len = 30
for i, ref_line in enumerate(analysis_lines):
    if len("".join(ref_line)) > max_line_len:
        report_lines.append(f"TOO LONG {i+1} {ref_line}")

with open(report_file, "w") as report_descriptor:
    for line in report_lines:
        report_descriptor.write(line + "\n")
