import random
import json
import os
import time

from config import PROGRESSION_FILE, IMAGES_MAPPING_FILE
from config import TEST, BURNING_SIZE


class ChainUnitType:
    type_key = "type_key"
    type_feature = "type_feature"
    mode_open = "mode_open"
    mode_question = "mode_question"
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


class ChainUnit:
    def __init__(
        S,
        text,
        type=None,
        mode=None,
        position=None,
        order_no=None,
        extra=None,
        preferred_position=None,
        feature_options=False,
        hint=False,
        font=ChainUnitType.font_utf,
    ):

        S.text = text
        S.type = type
        S.mode = mode
        S.position = position
        S.order_no = order_no
        S.font = font
        S.extra = extra
        S.hint = hint
        S.feature_options = feature_options


class ChainedFeature:
    def __init__(S, entity, features):
        S.entity = entity
        # TODO COMMON ABBREVATIONS
        S.features = [_ if ">DICT>" not in _ else _.replace(">DICT>","")[:50] for _ in features ]
        S.code_mode = False
        S.info = ""
        S.original_len = 1
        S.hints = [False for _ in range(10)]
        S.feature_level = 0
        S.feature_errors = []
        S.cummulative_error = 0
        S.decreased = False
        S.rised = False
        S.review = False
        S.attached_image = ""
        S.basic_timing_per_level = {0: 45, 1: 30, 2: 30}

    def set_mode(S, unit_type):

        if S.feature_level == 0:
            return ChainUnitType.mode_open
        elif S.feature_level >= 1 and unit_type == ChainUnitType.type_feature:
            return ChainUnitType.mode_question
        else:
            return ChainUnitType.mode_open

    def ask_for_image(S):
        if S.attached_image and S.feature_level < 2:
            return S.attached_image
        else:
            return None

    def set_extra(S, unit_type):
        return ChainUnitType.extra_focus

    def get_timing(S):
        if S.feature_level == 0 and not S.check_hints():
            return S.basic_timing_per_level[S.feature_level] // 3
        else:
            return S.basic_timing_per_level[S.feature_level]

    def check_hints(S):
        hints_set = True
        if S.review:
            return True
        for i in range(len(S.features)):
            if not S.hints[i]:
                hints_set = False
        return hints_set

    def recount_hints(S):
        if not S.check_hints():
            S.feature_level = 0
            S.decreased = True

    def try_set_random_entity(S):
        if S.review:
            S.entity = "["+random.choice(S.features)+"]"

    def get_context(S):
        '''Both get features, and tick-like method'''
        S.try_set_random_entity()
        features = [
            ChainUnit(
                _,
                ChainUnitType.type_feature,
                S.set_mode(ChainUnitType.type_feature),
                ChainUnitType.position_features,
                i,
                preferred_position=i,
                feature_options=S.review,
                hint=S.hints[i],
                extra=S.set_extra(ChainUnitType.type_feature),
            )
            for (i, _) in enumerate(S.features)
        ]
        return features

    def register_error(S, error_index):
        if error_index < len(S.feature_errors):
            S.feature_errors[error_index] += 1
            S.cummulative_error += 1

    def register_hint(S, hint_index, hint_x_rel, hint_y_rel):
        if hint_index < len(S.hints):
            S.hints[hint_index] = [hint_x_rel, hint_y_rel]

    def decrease_errors(S):
        if S.cummulative_error > 1:
            S.cummulative_error //= 2
        else:
            S.cummulative_error = 0

        for i in range(len(S.feature_errors)):
            error = S.feature_errors[i]
            if error > 1:
                S.feature_errors[i] //= 2
            else:
                S.feature_errors[i] = 0

    def get_main_title(S):
        return S.entity

    def register_progress(S, is_solved=False):
        timing = S.basic_timing_per_level[S.feature_level]
        level = S.feature_level
        if is_solved:
            if level != 0:
                S.basic_timing_per_level[S.feature_level] = (
                    timing + 2 if timing < 40 else 40
                )

            S.feature_level = level + 1 if level < 2 else 2
            S.rised = True
            S.decreased = False
        else:
            if level != 0:
                S.basic_timing_per_level[S.feature_level] = (
                    timing - 2 if timing > 25 else 25
                )
            S.feature_level = level - 1 if level > 0 else 0
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


class FeaturesChain:
    def __init__(S, chain_no, features, is_review_requires=True):
        S.chain_no = chain_no
        S.features = features

        if is_review_requires:
            S.features.append(S.create_review_chain(S.features))
            S.features[-1].review = True
            S.features[-1].original_len = len(S.features[-1].features)

        S.progression_level = 0
        S.errors_mapping = [[0 for _ in range(10)] for j in range(5)]
        S.hints_mapping = [[False for _ in range(10)] for j in range(5)]
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
        S.max_error = max(
            [max(feature.feature_errors, default=0) for feature in S.features],
            default=0,
        )
        S.cummulative_error = sum(sum(feature.feature_errors)
                                  for feature in S.features)

    def set_hints(S, hints_mapping):
        S.hints_mapping = hints_mapping
        all_hints_set = True
        for feature, feature_hints in zip(S.features, S.hints_mapping):
            feature.hints = feature_hints

    def update_errors(S, register_new=False):
        if register_new:
            S.fresh_errors += 1

        for error_index, (feature, _) in enumerate(zip(S.features, S.errors_mapping)):
            S.errors_mapping[error_index] = feature.feature_errors
        S.max_error = max(
            [max(feature.feature_errors, default=0) for feature in S.features],
            default=0,
        )
        S.cummulative_error = sum(sum(feature.feature_errors)
                                  for feature in S.features)

    def update_hints(S):
        for hint_index, (feature, _) in enumerate(zip(S.features, S.hints_mapping)):
            S.hints_mapping[hint_index] = feature.hints

    def get_worst_features(S, features_no=1):
        sorted_by_mistake = sorted(
            S.features, key=lambda _: _.cummulative_error, reverse=True
        )
        return sorted_by_mistake[:features_no]

    def initialize_images(S, images_list):
        for i, feature in enumerate(images_list):
            i2 = (i + 1) % len(images_list)
            # print(i, i2, len(images_list))
            if i < len(S.features):
                S.features[i].attached_image = [
                    images_list[i], images_list[i2]]
            else:
                break

        # for image, feature in zip(images_list, S.features):
        # feature.attached_image = image
        S.features[-1].attached_image = images_list

    def get_next_feature(S):
        S.features[S.active_position].recount_hints()

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
        S.features[S.active_position].recount_hints()
        return S.features[S.active_position]


class ChainedModel:
    def __init__(S, chains):
        S.chains = chains
        S.active_chain = None
        S.old_limit = 2
        S.new_limit = 2
        S.mistakes_trigger = False
        S.mistakes_chain = []
        S.burning_chain = []
        S.chain_alter_notify = False
        S.skip_first_alter = True

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
            S.chains.sort(key=lambda _: _.progression_level +
                          _.last_review_urge * 0.25)
        else:
            S.chains.sort(key=lambda _: _.progression_level)
            if not S.new_limit:

                S.old_limit = 2
                S.new_limit = 2
        S.dump_results(PROGRESSION_FILE)

    def add_mistake_chains(S):

        if not S.active_chain:
            return

        worst_features = S.active_chain.get_worst_features(features_no=2)

        for feature in worst_features:
            if feature.cummulative_error == 0 or feature in S.mistakes_chain:
                continue
            S.mistakes_chain.append(feature)

        S.mistakes_chain.sort(key=lambda _: _.cummulative_error, reverse=True)

    def change_active_chain(S):
        if not S.skip_first_alter:
            S.chain_alter_notify = True
        else:
            S.skip_first_alter = False

        S.add_mistake_chains()

        S.resample()

        if S.mistakes_trigger:
            S.mistakes_trigger = False

            if len(S.mistakes_chain) > 5:
                mistakes_to_work, S.mistakes_chain = (
                    S.mistakes_chain[:5],
                    S.mistakes_chain[5:],
                )

                for mistake in mistakes_to_work:
                    mistake.decrease_errors()
                S.active_chain = FeaturesChain(
                    -1, mistakes_to_work, is_review_requires=False
                )
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
        while len(options) < 10:
            try:
                if sample.type == ChainUnitType.type_feature:
                    random_chain = random.choice(
                        random.choice(S.chains).features)

                    if random_chain.review:
                        continue

                    if sample.feature_options:
                        selected = random_chain.entity
                    else:
                        selected = random.choice(random_chain.features)
                    options.append(selected)

            except Exception as e:
                continue

        seed = time.time()
        random.seed(seed)

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
        return len(S.burning_chain) >= BURNING_SIZE

    def get_burning_features_list(S):
        features_list = []
        #S.burning_chain = random.sample(S.burning_chain, BURNING_SIZE)
        for feature in S.burning_chain:
            features_list.append([feature.entity])
            if isinstance(feature.attached_image, list):
                features_list[-1] += feature.features[:feature.original_len] + [feature.attached_image[0]]
            else:
                features_list[-1] += feature.features[:feature.original_len] + [feature.attached_image]
        S.burning_chain = []
        return features_list

    def dump_results(S, progression_file):
        backup = {}
        for chain in S.chains:
            backup[chain.chain_no] = [
                chain.progression_level,
                chain.last_review_urge,
                {"errors": chain.errors_mapping},
                {"hints": chain.hints_mapping},
            ]

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
            with open(progression_file, encoding="UTF-8") as saved_prgress:
                progress = json.load(saved_prgress)

            if progress:
                for chain in S.chains:
                    if chain.chain_no not in progress:
                        print(f"chain {chain.chain_no} not in progress")
                        errors_mapping = [
                            [0 for _ in range(10)] for j in range(5)]
                        hints_mapping = [
                            [False for _ in range(10) for j in range(5)]]

                        progress[chain.chain_no] = [
                            0,
                            0,
                            {"errors": chain.errors_mapping},
                            {"hints": chain.hints_mapping},
                        ]

                    chain.progression_level = progress[chain.chain_no][0]
                    chain.last_review_urge = progress[chain.chain_no][1]

                    if chain.progression_level > 0:
                        chain.ascend()

                    errors_mapping = []
                    hints_mapping = []

                    # ERROR 1
                    outdated_format = (
                        len(progress[chain.chain_no]) != 4
                        or not isinstance(progress[chain.chain_no][2], dict)
                        or not isinstance(progress[chain.chain_no][3], dict)
                    )
                    if outdated_format or "errors" not in progress[chain.chain_no][2]:
                        print(f"errors not in {chain.chain_no}")
                        errors_mapping = [
                            [0 for _ in range(10)] for j in range(5)]
                    else:
                        errors_mapping = progress[chain.chain_no][2]["errors"]

                    if outdated_format or "hints" not in progress[chain.chain_no][3]:
                        print(f"hints not in {chain.chain_no}")
                        hints_mapping = [
                            [False for _ in range(10)] for j in range(5)]
                    else:
                        hints_mapping = progress[chain.chain_no][3]["hints"]

                    chain.set_errors(errors_mapping)
                    chain.set_hints(hints_mapping)

            return True
        return False

    def get_chains_progression(S):
        minimal_level = min(
            S.chains, key=lambda _: _.progression_level
        ).progression_level
        mastered = len(
            list(filter(lambda _: _.progression_level > minimal_level, S.chains))
        )
        return f"{minimal_level}x {mastered}/{len(S.chains)}"

    def get_active_chain(S):

        return S.active_chain
