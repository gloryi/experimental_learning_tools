import os

#LEARNING_SET_FOLDER = os.path.join(os.getcwd(), "learning_sets", "hsk_set")
LEARNING_SET_FOLDER = os.path.join(os.getcwd(), "learning_sets", "hanzi_set")
#LEARNING_SET_FOLDER = os.path.join(os.getcwd(), "learning_sets", "peg_wiki")

META_MINOR = os.path.join(os.getcwd(), "datasets", "semantical_affirmations.csv")

TEST_LANG_DATA = os.path.join(LEARNING_SET_FOLDER, "features.csv")
PROGRESSION_FILE = os.path.join(LEARNING_SET_FOLDER, "saved_progress.json")
IMAGES_MAPPING_FILE = os.path.join(LEARNING_SET_FOLDER, "images_mapping.json")
META_SCRIPT = os.path.join(LEARNING_SET_FOLDER, "context.csv")

BURNER_APP = os.path.join(os.getcwd(), "burner", "app.py")
BURNER_FILE = os.path.join(os.getcwd(), "burner", "data_to_burn.csv")

CHINESE_FONT = os.path.join(os.getcwd(), "fonts", "simhei.ttf")
CYRILLIC_FONT = os.path.join(os.getcwd(), "fonts", "Inter_font.ttf")
BPM = 10

W_OFFSET = 200
H_OFFSET = 100

W = 1400 + W_OFFSET * 2
H = 800  + H_OFFSET * 2
