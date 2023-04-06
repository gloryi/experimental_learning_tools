import os
from collections import defaultdict
import pathlib
import json

images_outdir = os.path.join(os.getcwd(), "images_for_learn")

mapping_to_data = defaultdict(list)

images_prepared = []

for i in range(2500, 2759, 1):
    img_name = os.path.join(images_outdir, f"{i}.jpg")
    images_prepared.append(img_name)

images_prepared = images_prepared[: len(images_prepared) - len(images_prepared) % 5]

for I, i in enumerate(range(0, len(images_prepared), 5)):
    for j in range(5):
        mapping_to_data[I + 500].append(images_prepared[i + j])

with open("dataset_mappping_extra.json", "w") as tmpjson:
    json.dump(mapping_to_data, tmpjson)

exit()


# images_outdir = os.path.join(os.getcwd(), "images_for_learn")
#
# images_for_work = [os.path.join(images_outdir, _) for _ in os.listdir(images_outdir)]
#
#
# for work_image in images_for_work[10:15]:
#     png_named = work_image.replace(".jpg", ".png")
#     os.system(f"convert {work_image} -resize 1800x1000 -background none -gravity center -extent 1800x1000 -vignette 100x100+0+0 {png_named}")
#     # image_out_name = os.path.join(images_outdir, f"{i}.jpg")
#     # os.system(f"convert {image_outsized} -resize 1400x800 -background white -gravity center -extent 1400x800 {image_out_name}")
#     # images_prepared.append(image_out_name)
images_dirs = []
images_dirs.append(os.path.join(os.getcwd(), "images_5_byhand_to_delet"))


images = []
for directory in images_dirs:
    images += [os.path.join(directory, _) for _ in os.listdir(directory)]

images = images[:2500]


images_prepared = []

for i, image_outsized in enumerate(images):
    image_out_name = os.path.join(images_outdir, f"{i+2500}.jpg")
    os.system(
        f"convert {image_outsized} -resize 1800x1000 -background white -gravity center -extent 1400x800 {image_out_name}"
    )
