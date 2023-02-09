import os
import random
from time import time

#preparation = True
preparation = False

LEARNING_FOLDERS = []
if not preparation:
    LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "personal_set"))
    LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "hsk_set"))
    LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "hsk_34"))
    LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "hanzi_set"))
    LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "hanzi_2"))
    #LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "latvian_set"))
    #LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "hsk_5"))
    #LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "hsk_6"))
else:
    LEARNING_FOLDERS.append(os.path.join(os.getcwd(), "learning_sets", "personal_set"))

random.seed(time())
LEARNING_SET_FOLDER = random.choice(LEARNING_FOLDERS)

META_MINOR = os.path.join(os.getcwd(), "datasets", "semantical_affirmations.csv")

TEST_LANG_DATA = os.path.join(LEARNING_SET_FOLDER, "features.csv")
PROGRESSION_FILE = os.path.join(LEARNING_SET_FOLDER, "saved_progress.json")
IMAGES_MAPPING_FILE = os.path.join(LEARNING_SET_FOLDER, "images_mapping.json")
META_ACTION = os.path.join(os.getcwd(), "action_affirmations.csv")
META_SCRIPT = os.path.join(LEARNING_SET_FOLDER, "context.csv")

HAPTIC_FEEDBACK_CMD = os.path.join(os.getcwd(), "controller_features", "example.sh")
HAPTIC_ERROR_CMD = os.path.join(os.getcwd(), "controller_features", "error.sh")
HAPTIC_CORRECT_CMD = os.path.join(os.getcwd(), "controller_features", "correct.sh")

BURNER_APP = os.path.join(os.getcwd(), "burner", "app.py")
BURNER_FILE = os.path.join(os.getcwd(), "burner", "data_to_burn.csv")

CHINESE_FONT = os.path.join(os.getcwd(), "fonts", "simhei.ttf")
CYRILLIC_FONT = os.path.join(os.getcwd(), "fonts", "NotoSans-SemiBold.ttf")

BPM = 10

W_OFFSET = 200
H_OFFSET = 100

W = 2400 + W_OFFSET * 2
H = 1240  + H_OFFSET * 2
