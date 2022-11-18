import csv

def extract_bijection_csv(path_to_file):
    bijection = [] 
    with open(path_to_file) as datafile:
        reader = csv.reader(datafile)
        for line in reader:
            A, B = line
            yield [A,B]

