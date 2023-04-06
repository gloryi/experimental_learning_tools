# from tika import parser
#
# def extract_pdf_text_raw(pdffile_location):
#     raw = parser.from_file(pdffile_location)
#     return raw
#
# text = extract_pdf_text_raw("/mnt/X/WORKSHOP/Lit/ToBeReaded/RawText/Law/book1_3.pdf")
# print(text)

import os
from collections import defaultdict

with open(os.path.join(os.getcwd(), "raw_chinese")) as glyphs_set:
    text = glyphs_set.read()

freq_dict = defaultdict(int)

for symbol in text:
    freq_dict[symbol] += 1

print(len(text))
print(len(freq_dict))
