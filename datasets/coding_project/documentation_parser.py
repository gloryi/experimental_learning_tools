import csv
import json
import os
import random
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import bs4

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

def get_only_text(elem):
    for item in elem.children:
        if isinstance(item,bs4.element.NavigableString):
            yield item
        else:
            yield from get_only_text(item)

processed_urls = set()
def parse_pyindex_recursively(root, page_index, max_depth = 5):
    global processed_urls

    if max_depth == 0:
        return []

    page_url = root+page_index
    if page_url not in processed_urls:
        processed_urls.add(page_url)
    else:
        return []

    #  print(page_url)
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html5lib')

    processed = []
    for entity in soup.findAll('dl', attrs = {'class': 'py'}):
        for function, description in zip(entity.findAll('dt', attrs = {'class': 'sig sig-object py'}),
                                         entity.findAll('p')):


            func = ''.join(get_only_text(function)).replace("\n","").replace("¶","")
            descr = ''.join(get_only_text(description)).replace("\n","").replace("¶","")
            if processed and len(processed[-1]) < 6:
                processed[-1] += [func, ">DICT>"+descr]
            else:
                processed.append(["***" + page_index, "#CODE#", func, ">DICT>"+descr])




    limit = 100 
    print(page_url)
    for int_url in soup.findAll('a', attrs = {'class' : 'reference internal'}):
        int_url = '/'+int_url['href']
        if "#" in int_url:
            continue
        #  limit -= 1
        processed += parse_pyindex_recursively(root, int_url, max_depth=max_depth-1)
        if not limit:
            break

    return processed




root_url = "https://docs.python.org/3/library" 
index_page = "/index.html"

LEARNING_SETS_DIR = "/mnt/X/WORKSHOP/Scripts/chained_learning/learning_sets"
LEARNING_SET = "python_codes_2"
FEATURES_OUTPUT = os.path.join(LEARNING_SETS_DIR, LEARNING_SET, "raw_features.csv") 

processed = parse_pyindex_recursively(root_url, index_page)
print(processed)
list_to_csv(FEATURES_OUTPUT, processed)
