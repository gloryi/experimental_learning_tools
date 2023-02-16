import random
import json
import os
from config import PROGRESSION_FILE, IMAGES_MAPPING_FILE
from config import TEST

class ChainUnitType():
    type_key = "type_key"
    type_feature = "type_feature"
    mode_open =  "mode_open"
    mode_question =  "mode_question"
    mode_active_question = "mode_active_question"
    mode_hidden = "mode_hidden"
    mode_highligted = "mode_highligted"
    extra_focus = "extra_focus"
    position_subtitle = "position_subtitle"
    position_features = "position_features"
    position_keys = "position_keys"
    font_cyrillic = "font_cyrillic"
    font_utf = "font_utf"
    font_short_utf = "font_short_utf"

class ChainUnit():
    def __init__(S,
                 text,
                 type = None,
                 mode = None,
                 position = None,
                 order_no = None,
                 extra = None,
                 preferred_position = None,
                 font = ChainUnitType.font_utf):

        S.text = text
        S.type = type
        S.mode = mode
        S.position = position
        S.order_no = order_no
        S.font = font
        S.preferred_position = preferred_position
        S.extra = extra

class ChainedFeature():
    def __init__(S, entity, features):
        S.entity = entity
        S.features = [_[:20] for _ in features]
        S.feature_level = 0
        S.feature_errors = []
        S.cummulative_error = 0
        S.decreased = False
        S.rised = False
        S.review = False
        S.attached_image = ""
        S.basic_timing_per_level = {0:35,
                                       1:35,
                                       2:35}

    def set_mode(S, unit_type):
        if S.feature_level == 0:
            return ChainUnitType.mode_open
        elif S.feature_level >= 1 and unit_type == ChainUnitType.type_feature:
            return ChainUnitType.mode_question
        else:
            return ChainUnitType.mode_open

    def ask_for_image(S):
        if S.attached_image and S.feature_level <2:
            #if len(S.attached_image) <= 2:
            return S.attached_image
            #else:
                #return S.attached_image[0::2]
        else:
            return None

    def set_extra(S, unit_type):
        return ChainUnitType.extra_focus

    def get_timing(S):
        return S.basic_timing_per_level[S.feature_level]


    def get_context(S):
       features = [ChainUnit(_, ChainUnitType.type_feature,
                                 S.set_mode(ChainUnitType.type_feature),
                                 ChainUnitType.position_features, i,
                              preferred_position = i,
                             extra = S.set_extra(ChainUnitType.type_feature)) for (i,_) in enumerate(S.features)]
       return features

    def register_error(S, error_index):
        if error_index < len(S.feature_errors):
            S.feature_errors[error_index] += 1
            S.cummulative_error += 1

    def decrease_errors(S):
        if S.cummulative_error > 1:
            S.cummulative_error //= 2
        else:
            S.cummulative_error = 0

        for i in range(len(S.feature_errors)):
            error = S.feature_errors[i]
            if error > 1:
                S.feature_errors[i]//=2
            else:
                S.feature_errors[i] = 0


    def get_main_title(S):
        return S.entity

    def register_progress(S, is_solved = False):
        timing = S.basic_timing_per_level[S.feature_level]
        level = S.feature_level
        if is_solved:
            S.basic_timing_per_level[S.feature_level] = timing +5 if timing < 50 else 50
            S.feature_level = level + 1 if level < 2 else 2
            S.rised = True
            S.decreased = False
        else:
            S.basic_timing_per_level[S.feature_level] = timing -5 if timing > 30 else 30
            S.feature_level = level -1 if level > 0 else 0
            S.decreased = True
            S.rised = False

    def select(S):
        S.rised = False
        S.decreased = False

    def deselect(S):
        S.rised = False
        S.decreased = False

    def get_features_len(S):
        return len(S.keys)

    def __repr__(S):
        return f"{S.entity} | progress = {S.feature_level} | errors = {S.cummulative_error}"


class FeaturesChain():
    def __init__(S, chain_no, features, is_review_requires = True):
        S.chain_no = chain_no
        S.features = features

        if is_review_requires:
            S.features.append(S.create_review_chain(S.features))
            S.features[-1].review = True

        S.progression_level = 0
        S.errors_mapping = [[0 for _ in range(10)] for j in range(5)]
        S.max_error = 0
        S.cummulative_error = 0
        S.fresh_errors = 0
        S.last_review_urge = 0
        S.active_position = -1
        S.ascended = False

    def create_review_chain(S, features):
        entity = str(S.chain_no).rjust(3, "0")
        review_features = []
        for feature in features:
            review_features.append(feature.entity)
        return ChainedFeature(entity, review_features)

    def ascend(S):
        for feature in S.features:
            feature.feature_level = 2
            feature.deselect()

    def set_errors(S, errors_mapping):
        S.errors_mapping = errors_mapping
        for feature, feature_errors in zip(S.features, S.errors_mapping):
            feature.feature_errors = feature_errors
            feature.cummulative_error = sum(feature_errors)
        S.max_error = max([max(feature.feature_errors, default=0) for feature in S.features], default=0)
        S.cummulative_error = sum(sum(feature.feature_errors) for feature in S.features)

    def update_errors(S, register_new = False):
        if register_new:
            S.fresh_errors += 1

        for error_index, (feature, _) in enumerate(zip(S.features, S.errors_mapping)):
            S.errors_mapping[error_index] = feature.feature_errors
        S.max_error = max([max(feature.feature_errors, default = 0) for feature in S.features], default=0)
        S.cummulative_error = sum(sum(feature.feature_errors) for feature in S.features)

    def get_worst_features(S, features_no = 1):
        sorted_by_mistake = sorted(S.features,key = lambda _ : _.cummulative_error, reverse = True)
        return sorted_by_mistake[:features_no]


    def initialize_images(S, images_list):
        for i, feature in enumerate(images_list):
            i2 = (i+1)%len(images_list)
            #print(i, i2, len(images_list))
            if i < len(S.features):
                S.features[i].attached_image = [images_list[i], images_list[i2]]
            else:
                break

        #for image, feature in zip(images_list, S.features):
            #feature.attached_image = image
        S.features[-1].attached_image = images_list

    def get_next_feature(S):
        level = S.features[S.active_position].feature_level
        is_fallback = S.features[S.active_position].decreased
        is_up = S.features[S.active_position].rised
        if level == 0 and is_fallback:
            return S.features[S.active_position]
        if level == 1:
            return S.features[S.active_position]
        if level == 2 and not is_up:
            return S.features[S.active_position]

        S.features[S.active_position].deselect()
        S.active_position += 1
        if S.active_position >= len(S.features):
            S.active_position = 0
            if S.fresh_errors <= 3:
                S.progression_level += 1
            elif S.fresh_errors <= 6:
                S.progression_level = S.progression_level
            else:
                S.progression_level -= 1
                if S.progression_level < 0:
                    S.progression_level = 0

            S.fresh_errors = 0

            return None
        S.features[S.active_position].select()
        return S.features[S.active_position]


class ChainedModel():
    def __init__(S, chains):
        S.chains = chains
        S.active_chain = None
        S.old_limit = 2
        S.new_limit = 2
        S.mistakes_trigger = False
        S.mistakes_chain = []
        S.burning_chain = []

        is_restored = S.restore_results(PROGRESSION_FILE)

        if not is_restored:
            S.active_chain = S.get_active_chain()
            S.dump_results(PROGRESSION_FILE)
        else:
            S.change_active_chain()

        S.attach_images(IMAGES_MAPPING_FILE)

    def resample(S):

        if len(S.mistakes_chain) >= 5:
            S.mistakes_trigger = True

        for chain in S.chains:
            if chain.progression_level > 0:

                chain.last_review_urge = chain.last_review_urge - 1

        if S.old_limit:
            S.chains.sort(key = lambda _ : _.progression_level + _.last_review_urge * 0.25)
        else:
            S.chains.sort(key = lambda _ : _.progression_level)
            if not S.new_limit:

                S.old_limit = 2
                S.new_limit = 2
        S.dump_results(PROGRESSION_FILE)

    def add_mistake_chains(S):

        if not S.active_chain:
            return

        worst_features = S.active_chain.get_worst_features(features_no = 2)

        for feature in worst_features:
            if feature.cummulative_error == 0 or feature in S.mistakes_chain:
                continue
            S.mistakes_chain.append(feature)

        S.mistakes_chain.sort(key = lambda _ : _.cummulative_error, reverse = True)

    def change_active_chain(S):

        S.add_mistake_chains()

        S.resample()


        if S.mistakes_trigger:
            S.mistakes_trigger = False

            if len(S.mistakes_chain) > 5:
                mistakes_to_work, S.mistakes_chain = S.mistakes_chain[:5], S.mistakes_chain[5:]

                for mistake in mistakes_to_work:
                    mistake.decrease_errors()
                S.active_chain =  FeaturesChain(-1, mistakes_to_work, is_review_requires = False)
                return

        S.active_chain = S.chains[0]

        if S.active_chain.last_review_urge < 0:
            S.old_limit -= 1
        else:
            S.new_limit -= 1

        S.active_chain.last_review_urge = 0
        S.active_chain.update_errors()

    def get_options_list(S, sample):
        options = [sample.text]
        while len(options) < 6:
            try:
                random_features_chain = random.choice
                random_chain = random.choice(random.choice(S.chains).features)
                preferred_position = sample.preferred_position
                if sample.type == ChainUnitType.type_feature:
                    if preferred_position is None or preferred_position >= len(random_chain.features):
                        selected = random.choice(random_chain.features)
                    else:
                        selected = random_chain.features[preferred_position]
                    options.append(selected)
            except Exception as e:
                continue
        random.shuffle(options)
        return options

    def get_next_feature(S):
        if not S.active_chain:
            S.change_active_chain()

        next_feature = S.active_chain.get_next_feature()
        if not next_feature:
            S.change_active_chain()
            next_feature = S.active_chain.get_next_feature()

        if not next_feature.review and not next_feature in S.burning_chain:
            S.burning_chain.append(next_feature)

        return next_feature

    def is_burning(S):
        return len(S.burning_chain) >= 25

    def get_burning_features_list(S):
        features_list = []
        S.burning_chain = random.sample(S.burning_chain, 25)
        for feature in S.burning_chain:
            features_list.append([feature.entity])
            features_list[-1] += [feature.features[0]]
        S.burning_chain = []
        return features_list

    def dump_results(S, progression_file):
        if TEST:
            return
        backup = {}
        for chain in S.chains:
            backup[chain.chain_no] = [chain.progression_level, chain.last_review_urge, chain.errors_mapping]
        with open(progression_file, "w") as current_progress:
            json.dump(backup, current_progress, indent=2)

    def attach_images(S, images_file):
        if os.path.exists(images_file):
            images = {}
            with open(images_file) as images_ordered:
                images = json.load(images_ordered)
            if images:
                for chain in S.chains:
                    if chain.chain_no in images:
                        chain.initialize_images(images[chain.chain_no])
                    else:
                        print(f"Chain {chain.chain_no} have no image prepared")

    def restore_results(S, progression_file):
        if os.path.exists(progression_file):
            progress = {}
            with open(progression_file) as saved_prgress:
                progress = json.load(saved_prgress)
            if progress:
                for chain in S.chains:
                    if chain.chain_no not in progress:
                        errors_mapping = [[0 for _ in range(10)] for j in range(5)]
                        progress[chain.chain_no] = [0, 0, chain.errors_mapping]
                    chain.progression_level = progress[chain.chain_no][0]
                    chain.last_review_urge = progress[chain.chain_no][1]
                    if chain.progression_level > 0:
                        chain.ascend()
                    errors_mapping = []
                    if len(progress[chain.chain_no]) == 2:
                        errors_mapping = [[0 for _ in range(10)] for j in range(5)]
                    else:
                        errors_mapping = progress[chain.chain_no][2]

                    chain.set_errors(errors_mapping)

            return True
        else:
            return False

    def get_chains_progression(S):
        minimal_level = min(S.chains, key = lambda _ : _.progression_level).progression_level
        mastered = len(list(filter(lambda _: _.progression_level > minimal_level, S.chains)))
        return f"{minimal_level}x {mastered}/{len(S.chains)}"


    def get_active_chain(S):

        return S.active_chain
