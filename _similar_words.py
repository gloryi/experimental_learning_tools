from mnemonic import Mnemonic
import eng_to_ipa as ipa
import epitran
import random

print(ipa.convert("zhèng heart solo"))

# exit()

features = "top sky heart root square big labor old relation appear beginning"
features = features.split()

# converted = ipa.convert(features)


# print(*features)
# print(converted)
# exit()
# features_chain = {}

# for word in keys.split():
# features_chain[word] = ipa.convert(word)

# keys_dict = {}
# mnemo = Mnemonic("english")
# words = mnemo.generate(strength=256)

words = []

with open("rus_semantics.csv") as nounfile:
    for line in nounfile:
        if len(line) >= 6 and len(line) < 10:
            words.append(line[:-1])


# random.shuffle(words)
# words = words[:3000]
epi = epitran.Epitran("rus-Cyrl")

keys_dict = {}
for word in words:
    keys_dict[epi.transliterate(word)] = word

target_pairs = []


# for word in words.split():
# keys_dict[word] = ipa.convert(word)

# for feature_image in features:
# feature_translated = features[feature_image]


for f1, f2 in zip(features[:-1], features[1:]):
    ft1, ft2 = ipa.convert(f1), ipa.convert(f2)
    ft1s, ft2s = set(ft1), set(ft2)
    cross_1 = lambda _: len(ft1s.intersection(set(_[: len(_) // 2])))
    cross_2 = lambda _: len(ft2s.intersection(set(_[len(_) // 2 :])))
    cross = lambda _: cross_1(_) + cross_2(_)
    # print(f"{f1}+{f2} = {cross_key_words}")
    closest_key = max(keys_dict, key=cross)
    target_pairs.append([f1, f2, keys_dict[closest_key]])
    # print(f1)
    # print(ft1s)
    # print(ft1s.intersection(closest_key[:len(closest_key)//2]))
    # print(closest_key[:len(closest_key)//2])
    # print(keys_dict[closest_key])
    # print(closest_key[len(closest_key)//2:])
    # print(ft2s.intersection(closest_key[len(closest_key)//2:]))
    # print(ft2s)
    # print(f2)
    # print()
    # print(keys_dict[closest_key])
    del keys_dict[closest_key]

for p in target_pairs:
    f1, f2, k = p
    print(f"{f1} => {k} => {f2}")
