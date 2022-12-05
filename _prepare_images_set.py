import os
import random
import json
from collections import defaultdict

images_dirs = []
images_dirs.append(os.path.join(os.getcwd(), "images"))
images_dirs.append(os.path.join(os.getcwd(), "images2"))
images_dirs.append(os.path.join(os.getcwd(), "images3"))
images_dirs.append(os.path.join(os.getcwd(), "images4"))


images = []
for directory in images_dirs:
    images += [os.path.join(directory, _) for _ in  os.listdir(directory)]

images = images[:2500]

images_outdir = os.path.join(os.getcwd(), "images_for_learn")

images_prepared = []

for i, image_outsized in enumerate(images):
    image_out_name = os.path.join(images_outdir, f"{i}.jpg")
    os.system(f"convert {image_outsized} -resize 1400x800 -background white -gravity center -extent 1400x800 {image_out_name}")
    images_prepared.append(image_out_name)

random.shuffle(images_prepared)


mapping_to_data = defaultdict(list) 

for I, i in enumerate(range(0, len(images_prepared), 5)):
    for j in range(5):
        mapping_to_data[I].append(images_prepared[i+j])

with open("dataset_mapping_2500.json", "w") as jsonfile:
    json.dump(mapping_to_data, jsonfile)

