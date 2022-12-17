import os
#TEST_LANG_DATA = os.path.join(os.getcwd(), "test_semantics.csv")
#TEST_LANG_DATA    = os.path.join(os.getcwd(), "glyphs_set.csv")

#TEST_LANG_DATA = os.path.join(os.getcwd(), "datasets", "hanzi_prepared.csv")
TEST_LANG_DATA = os.path.join(os.getcwd(), "datasets", "hanzi_hsk_complete_set.csv")
PROGRESSION_FILE = os.path.join(os.getcwd(), "hanzi_progress.json")
META_SCRIPT = os.path.join(os.getcwd(), "datasets", "hanzi_affirmations.csv")
IMAGES_MAPPING_FILE = os.path.join(os.getcwd(), "dataset_mapping_2500.json")
CHINESE_FONT = os.path.join(os.getcwd(), "fonts", "simhei.ttf")
CYRILLIC_FONT = os.path.join(os.getcwd(), "fonts", "Inter_font.ttf")
BPM = 10

W_OFFSET = 200
H_OFFSET = 100

W = 1400 + W_OFFSET * 2
H = 800  + H_OFFSET * 2
