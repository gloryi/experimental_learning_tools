import os
import subprocess
import random
from time import time
from collections import OrderedDict

TEST = True
TEST = False
PREPR = False
PREPR = True

sets_prefix = os.path.join(os.getcwd(), "learning_sets")

def locate_set(_):
    return os.path.join(sets_prefix, _)


LEARNING_FOLDERS = []
if not PREPR and not TEST:
    # LEARNING_FOLDERS.append(locate_set("latvian_set"))

    #  LEARNING_FOLDERS.append(locate_set("python_modules"))
    #  LEARNING_FOLDERS.append(locate_set("vim_shortcuts"))

    LEARNING_FOLDERS.append(locate_set("hanzi_set"))
    LEARNING_FOLDERS.append(locate_set("hsk_set"))
    LEARNING_FOLDERS.append(locate_set("hsk_rad"))

    #  LEARNING_FOLDERS.append(locate_set("hanzi_2"))
    #  LEARNING_FOLDERS.append(locate_set("hsk_34"))
    #  LEARNING_FOLDERS.append(locate_set("hsk_pin"))

#
    # LEARNING_FOLDERS.append(locate_set("hsk_5"))
    # LEARNING_FOLDERS.append(locate_set("hsk_6"))
elif not TEST:
    LEARNING_FOLDERS.append(locate_set("personal_set"))
else:
    LEARNING_FOLDERS.append(locate_set("test_set"))


random.seed(time())
LEARNING_SET_FOLDER = random.choice(LEARNING_FOLDERS)

META_MINOR = os.path.join(os.getcwd(), "datasets", "semantical_affirmations.csv")

TEST_LANG_DATA = os.path.join(LEARNING_SET_FOLDER, "features.csv")
PROGRESSION_FILE = os.path.join(LEARNING_SET_FOLDER, "saved_progress.json")
IMAGES_MAPPING_FILE = os.path.join(LEARNING_SET_FOLDER, "images_mapping.json")
META_ACTION = os.path.join(
    "/home/gloryi/Documents/SpecialFiles", "action_affirmations.csv"
)
META_ACTION_STACK = OrderedDict()
META_ACTION_STACK["*** 1XBACK ***"] = []
META_ACTION_STACK["*** 1XKEYS ***"] = []
META_ACTION_STACK["*** 1XTEXT ***"] = []
META_ACTION_STACK["*** IBACK ***"] = []
META_ACTION_STACK["*** PERM ***"] = []
META_ACTION_STACK["*** OUT ***"] = []
META_SCRIPT = os.path.join(LEARNING_SET_FOLDER, "context.csv")

HAPTIC_PATH = "/home/gloryi/Documents/SpecialFiles/xbox_haptic/haptic_ultimate"
DEVICE_NAME = "/dev/input/by-id/usb-Microsoft_Controller_7EED82417161-event-joystick"

def HAPTIC_FEEDBACK(lower_freq=500, higher_freq=50000, duration=995):
    command = " ".join([HAPTIC_PATH, DEVICE_NAME,
                        str(lower_freq), str(higher_freq), str(duration)])
    subprocess.Popen(command, shell=True)

BURNER_APP = os.path.join(os.getcwd(), "burner", "app.py")
BURNER_FILE = os.path.join(os.getcwd(), "burner", "data_to_burn.csv")

CHINESE_FONT = os.path.join(os.getcwd(), "fonts", "simhei.ttf")
CYRILLIC_FONT = os.path.join(os.getcwd(), "fonts", "NotoSans-SemiBold.ttf")

BPM = 5

W_OFFSET = 200
H_OFFSET = 100

W = 2400 + W_OFFSET * 2
H = 1240 + H_OFFSET * 2 - 11

BURNING_SIZE = 20
# BURNING_SIZE = 5
