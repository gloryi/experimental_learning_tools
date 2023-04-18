import csv
import json
import os
import random
from tqdm import tqdm

def csv_to_list(target_path):
    with open(target_path, "r") as infile:
        reader = csv.reader(infile)
        return list(_ if len(_) > 1 else _[0] for _ in reader)

def list_to_csv(target_path, data):
    if not data:
        print(data) 
        raise Exception(f"data for {target_path} corrupted")

    with open(target_path, "w") as outfile:
        writer = csv.writer(outfile)
        for line in data:
            writer.writerow(line)

def produce_fileslit_recur(root_dir, files_filter = None):
    fileslist = []
    for _r, _d, _f in os.walk(root_dir):
        for f in _f:
            if files_filter(f):
                fileslist.append(os.path.join(_r, f))
    return fileslist

def find_token_in_file(token, filepath, depth=5, filters = []):
    lines_stack = []
    long_comment = False
    with open(filepath, "r") as infile:


        for line in infile:
            #TMP HARDCODE FOR PYTHON
            if line.strip().startswith("\"\"\"") and line.strip().endswith("\"\"\"") and not len(line.strip())<=3:
                continue
            if long_comment and "\"\"\"" not in line:
                continue
            if long_comment and "\"\"\"" in line:
                long_comment = False
                continue
            if not long_comment and "\"\"\"" in line:
                long_comment = True
                continue

            if any(_(line) for _ in filters):
                continue
            # TMP HARDCODE FOR SUMBOLS
            line = line.replace("\n", "").replace(",","!COMA").replace("  ", "!DBSP").replace("\t", "!TAB")
            lines_stack.append(line)
            if len(lines_stack)>depth:
                lines_stack.pop(0)

            if len(lines_stack) == depth and token in lines_stack[len(lines_stack)//2]:
                return lines_stack
                #  return [_ for _ in range(5)]
    return []

def find_token_examples_in_dirs(token, dirslist, depth=5, filters=[], ntries = 3000):
    random.shuffle(dirslist)
    for random_file in dirslist:
        token_context = find_token_in_file(token, random_file, depth, filters)
        if token_context:
            return token_context, random_file
    return None, None

TOKENS_FILE = "python_tokens_1.csv"
tokens = csv_to_list(TOKENS_FILE)[:20]

CODEBASE_EXTENSION = ".py"
CODEBASE_FILTER = lambda _ : _.endswith(".py")
CODE_FILTERS = []
CODE_FILTERS.append(lambda _ : _.strip()=="")
#CODE_FILTERS.append(lambda _ : "def" in _)
#CODE_FILTERS.append(lambda _ : "class" in _)
CODE_FILTERS.append(lambda _ : len(_)>120)
CODE_FILTERS.append(lambda _ : _.strip().startswith("#"))
CODE_FILTERS.append(lambda _ : _.strip().startswith("\"\"\""))
CODE_FILTERS.append(lambda _ : _.strip().startswith("\'\'\'"))
CODE_FILTERS.append(lambda _ : _.strip().startswith(">>>"))
CODE_FILTERS.append(lambda _ : "import" in _)

CODEBASE_DIRS = []
#CODEBASE_DIRS.append("/usr/lib/python3.11")
#CODEBASE_DIRS.append("/usr/lib/python3")
CODEBASE_DIRS.append("/usr/lib/python3/dist-packages/numpy")
CODEBASE_DIRS.append("/usr/lib/python3/dist-packages/matplotlib")
CODEBASE_DIRS.append("/usr/lib/python3/dist-packages/django")
CODEBASE_DIRS.append("/usr/lib/python3/dist-packages/PyQt5")

LEARNING_SETS_DIR = "/mnt/X/WORKSHOP/Scripts/chained_learning/learning_sets"
LEARNING_SET = "python_codes_1"
FEATURES_OUTPUT = os.path.join(LEARNING_SETS_DIR, LEARNING_SET, "raw_features.csv") 

CODEBASE_FILES = []
for code_dir in CODEBASE_DIRS:
    CODEBASE_FILES += produce_fileslit_recur(code_dir, files_filter = CODEBASE_FILTER)

DPTH = 5

#tokens=["pairwise"]
extracted_context = []
#  for token in tokens:
for token in tqdm(tokens):

    examples_for_token = []
    for token_examples in range(5):
        token_context, selected_file = find_token_examples_in_dirs(token, CODEBASE_FILES, depth=DPTH, filters = CODE_FILTERS)
        if selected_file:
            selected_file = selected_file.replace("/usr/lib/python3/dist-packages/","")
        if token_context:
            examples_for_token.append([token+":"+selected_file] + ["#CODE#"] + token_context)

    if len(examples_for_token) == 5:
        extracted_context += examples_for_token
        #extracted_context.append(examples_for_token[0]+["#CODE#"]+examples_for_token[1:])

list_to_csv(FEATURES_OUTPUT, extracted_context)
