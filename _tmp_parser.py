import os
import csv
import re
import eng_to_ipa as ipa
import epitran
import random
from copy import deepcopy

def prepare_rus_keys(keysfile):
    words = []
    with open(keysfile) as nounfile:
        for line in nounfile:
            if(len(line) >= 6 and len(line)<12):
                words.append(line[:-1])

    epi = epitran.Epitran('rus-Cyrl')

    keys_dict = {}
    for word in words:
        keys_dict[epi.transliterate(word)] = word

    return keys_dict

def split_definition(definition):
    parts = re.split("[,;]",definition)
    parts = list(filter( lambda _ : len(_) < 12, parts))
    parts.sort(key = lambda _ : len(_))
    return parts[:5]

def extract_hanzi(hanzifile):
    extracted = []
    with open(os.path.join(os.getcwd(), hanzifile)) as cn_file:
        reader = csv.DictReader(cn_file, quotechar='"')
        headers = reader.fieldnames
        for line in reader:
            if "definition" not in line:
                continue
            charcter = line["charcter"]
            pin = line["pinyin"]
            definition = line["definition"]
            stroke_count = line["stroke_count"]
            if not definition:
                continue
            if not stroke_count:
                continue

            features = split_definition(definition)
            if not len(features) > 1:
                continue

            extracted.append([charcter, features[0]] + [pin] + features[1:])

    return extracted

def chain_two_features(f1, f2, mnemonic_dict):
    ft1, ft2 = ipa.convert(f1), ipa.convert(f2)
    ft1s, ft2s = set(ft1), set(ft2)
    cross_1 = lambda _ : len(ft1s.intersection(set(_[:len(_)//2])))
    cross_2 = lambda _ : len(ft2s.intersection(set(_[len(_)//2:])))
    cross = lambda _ : cross_1(_) + cross_2(_)
    closest_key = max(mnemonic_dict, key = cross)
    target_key = mnemonic_dict[closest_key]
    del mnemonic_dict[closest_key]
    return target_key

def create_chain(f_in, f_out, f_key, f_tail, mnemonic_dict, ready_in = ""):
    if not ready_in:
        in_key = chain_two_features(f_in, f_key, mnemonic_dict)
    else:
        in_key = ready_in
    out_key = chain_two_features(f_key, f_out, mnemonic_dict)
    features_tail = [f_key] + f_tail
    keys_tail = []
    for f1, f2 in zip(features_tail[:-1], features_tail[1:]):
        keys_tail.append(chain_two_features(f1, f2, mnemonic_dict))


    return [in_key, out_key] + keys_tail


semantic_keys = prepare_rus_keys("rus_semantics.csv")
chinese_units = extract_hanzi("hanziDB.csv")

random.shuffle(chinese_units)

BATCH_SIZE = 10
batches = []

for I in range(0, len(chinese_units), BATCH_SIZE):
    selected_units = chinese_units[I:min(I+BATCH_SIZE,len(chinese_units))]
    selected_units =[selected_units[-1]] + selected_units + [selected_units[0]]
    copied_keys = deepcopy(semantic_keys)
    batch_counter = I//BATCH_SIZE
    prev_in = ""
    original_in = ""

    for i in range(1,len(selected_units)-1, 1):
        batches.append([batch_counter])
        prev_f, next_f = selected_units[i-1][1], selected_units[i+1][1]
        current_f = selected_units[i][1]
        features_tail = selected_units[i][2:]
        if not prev_in:
            prev_k, next_k, *keys_tail = create_chain(prev_f, next_f, current_f, features_tail, copied_keys)
            original_in = prev_k
        else:
            prev_k, next_k, *keys_tail = create_chain(prev_f, next_f, current_f, features_tail, copied_keys, ready_in = prev_in)
        prev_in = next_k

        entity = selected_units[i][0]
        batches[-1] += [entity, prev_k, next_k, current_f]
        for feature, key in zip(features_tail, keys_tail):
            batches[-1] += [key, feature]

    batches[-1][3] = original_in

    if batch_counter > 8:
        break

with open("hanzi_prepared.csv", "w") as hanzi_prepared:
   csvwriter = csv.writer(hanzi_prepared)
   for line in batches:
       csvwriter.writerow(line)

