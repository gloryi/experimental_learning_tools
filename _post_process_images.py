import os
import pathlib 

images_outdir = os.path.join(os.getcwd(), "images_for_learn")

images_for_work = [os.path.join(images_outdir, _) for _ in os.listdir(images_outdir)]


for work_image in images_for_work[10:15]:
    png_named = work_image.replace(".jpg", ".png")
    os.system(f"convert {work_image} -resize 1800x1000 -background none -gravity center -extent 1800x1000 -vignette 100x100+0+0 {png_named}")
    # image_out_name = os.path.join(images_outdir, f"{i}.jpg")
    # os.system(f"convert {image_outsized} -resize 1400x800 -background white -gravity center -extent 1400x800 {image_out_name}")
    # images_prepared.append(image_out_name)
