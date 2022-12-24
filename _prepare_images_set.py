import os
import random
import json
from collections import defaultdict

images_dirs = []
images_dirs.append("/home/gloryi/Pictures/Windows 10 Spotlight")

sets_dir = os.path.join(os.getcwd(), "learning_sets")
set_dir = os.path.join(sets_dir, "peg_wiki")

TO_EXTRACT = 120
TARGET_NAME = os.path.join(set_dir, "images_mapping.json")

def extract_images_from_root(root_dir):
    images = []
    for _r, _d, _f in os.walk(root_dir):
        for f in _f:
            if ".png" or ".jpg" in f:
                images.append(os.path.join(_r, f))
    return images

images = []
for directory in images_dirs:
    images += extract_images_from_root(directory)

random.shuffle(images)

images_prepared = images[:TO_EXTRACT]


mapping_to_data = defaultdict(list) 

for I, i in enumerate(range(0, len(images_prepared), 5)):
    for j in range(5):
        mapping_to_data[I].append(images_prepared[i+j])

with open(TARGET_NAME, "w") as jsonfile:
    json.dump(mapping_to_data, jsonfile, indent=4)

