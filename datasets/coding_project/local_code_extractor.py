import csv
import json
import os
import random
from tqdm import tqdm

def csv_to_list(target_path):
    with open(target_path, "r") as infile:
        reader = csv.reader(infile)
        return list(_ if len(_) > 1 else _[0] for _ in reader)

def produce_fileslit_recur(root_dir, files_filter = None):
    fileslist = []
    for _r, _d, _f in os.walk(root_dir):
        for f in _f:
            if files_filter(f):
                fileslist.append(os.path.join(_r, f))
    return fileslist

def find_token_in_file(token, filepath, depth=5, filters = []):
    lines_stack = []
    with open(filepath, "r") as infile:
        for line in infile:
            if any(_(line) for _ in filters):
                continue

            lines_stack.append(line.replace("\n",""))
            if len(lines_stack)>depth:
                lines_stack.pop(0)

            if len(lines_stack) == depth and token in lines_stack[len(lines_stack)//2]:
                return lines_stack
    return []

def find_token_examples_in_dirs(token, dirslist, depth=5, filters=[], ntries = 3000):
    for attempt_n in range(ntries):
        random_file = random.choice(dirslist)
        token_context = find_token_in_file(token, random_file, depth, filters)
        if token_context:
            return token_context

TOKENS_FILE = "python_tokens_1.csv"
tokens = csv_to_list(TOKENS_FILE)

CODEBASE_EXTENSION = ".py"
CODEBASE_FILTER = lambda _ : _.endswith(".py")
CODE_FILTERS = []
CODE_FILTERS.append(lambda _ : _.strip()=="")
CODE_FILTERS.append(lambda _ : "def" in _)
CODE_FILTERS.append(lambda _ : "class" in _)
CODE_FILTERS.append(lambda _ : len(_)>120)
CODE_FILTERS.append(lambda _ : _.strip().startswith("#"))
CODE_FILTERS.append(lambda _ : _.strip().startswith("\"\"\""))
CODE_FILTERS.append(lambda _ : _.strip().startswith("\'\'\'"))
CODE_FILTERS.append(lambda _ : _.strip().startswith(">>>"))

CODEBASE_DIRS = []
CODEBASE_DIRS.append("/usr/lib/python3.11")
CODEBASE_DIRS.append("/usr/lib/python3")

CODEBASE_FILES = []
for code_dir in CODEBASE_DIRS:
    CODEBASE_FILES += produce_fileslit_recur(code_dir, files_filter = CODEBASE_FILTER)

for token in tokens:
    print(token)
    for token_examples in range(5):
        token_context = find_token_examples_in_dirs(token, CODEBASE_FILES, depth=10, filters = CODE_FILTERS)
        if token_context:
            for line in token_context:
                print(line)
            print("-"*10)
        else:
            print("X"*10)
            print("-"*10)
    print()
    print("*"*10)
    print()
