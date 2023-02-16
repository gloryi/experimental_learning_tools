import os
import random
import json
from collections import defaultdict

images_dirs = []
#images_dirs.append("/home/gloryi/Pictures/Windows 10 Spotlight")
#images_dirs.append("/home/gloryi/Pictures/FlickrSets")
images_dirs.append("/home/gloryi/Pictures/MovieShots")
images_dirs.append("/home/gloryi/Pictures/OldPhotos")
images_dirs.append("/home/gloryi/Pictures/Windows 10 Spotlight")

sets_dir = os.path.join(os.getcwd(), "learning_sets")
set_dir = os.path.join(sets_dir, "personal_set")

#set_dir = "/mnt/X/WORKSHOP/Scripts/stocks_learning_git/experimental_learning_tools"

TO_EXTRACT = 2000
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

print(f"target {set_dir}")
print(f"images registered {len(images)}")

random.shuffle(images)

images_prepared = images[:TO_EXTRACT]


mapping_to_data = defaultdict(list)

for I, i in enumerate(range(0, len(images_prepared), 5)):
    for j in range(5):
        mapping_to_data[I].append(images_prepared[i+j])

with open(TARGET_NAME, "w") as jsonfile:
    json.dump(mapping_to_data, jsonfile, indent=4)
