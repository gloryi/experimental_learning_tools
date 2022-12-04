import os
from csv import DictReader, writer

words_selected = []
lemma_header = "Lemma"
pos_header = "PoS"
freq_header = "Freq(ipm)"

with open(os.path.join(os.getcwd(), "datasets", freqrnc2011.csv")) as csvfile:
    reader = DictReader(csvfile,delimiter="\t")
    headers = reader.fieldnames
    print(headers)
    for line in reader:
        if line[pos_header] != "s":
            continue
        #if float(line[freq_header]) < 8.0:
            #continue
        words_selected.append([line[lemma_header], float(line[freq_header])])

words_selected.sort(key = lambda _ : _[1], reverse = True)
words_selected = [_[0] for _ in words_selected]

with open(os.path.join(os.getcwd(), "rus_semantics.csv"), "w") as lexical_file:
   csvwriter = writer(lexical_file)
   for line in words_selected:
       csvwriter.writerow([line])
