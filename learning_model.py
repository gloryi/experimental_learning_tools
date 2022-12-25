import random
import json
import os
from config import PROGRESSION_FILE, IMAGES_MAPPING_FILE

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
    def __init__(self,
                 text,
                 type = None,
                 mode = None,
                 position = None,
                 order_no = None,
                 extra = None,
                 preferred_position = None,
                 font = ChainUnitType.font_utf):

        self.text = text
        self.type = type
        self.mode = mode
        self.position = position
        self.order_no = order_no
        self.font = font
        self.preferred_position = preferred_position
        self.extra = extra

class ChainedFeature():
    def __init__(self, entity, features): 
        self.entity = entity
        self.features = [_[:20] for _ in features]
        self.feature_level = 0
        self.feature_errors = []
        self.cummulative_error = 0
        self.decreased = False
        self.rised = False
        self.review = False
        self.attached_image = "" 
        self.basic_timing_per_level = {0:35,
                                       1:35,
                                       2:35}

    def set_mode(self, unit_type):
        if self.feature_level == 0:
            return ChainUnitType.mode_open
        elif self.feature_level >= 1 and unit_type == ChainUnitType.type_feature:
            return ChainUnitType.mode_question
        else:
            return ChainUnitType.mode_open

    def ask_for_image(self):
        if self.attached_image and self.feature_level <2:
            return self.attached_image
        else:
            return ""

    def set_extra(self, unit_type):
        return ChainUnitType.extra_focus

    def get_timing(self):
        return self.basic_timing_per_level[self.feature_level]


    def get_context(self):
       features = [ChainUnit(_, ChainUnitType.type_feature,
                                 self.set_mode(ChainUnitType.type_feature),
                                 ChainUnitType.position_features, i,
                              preferred_position = i,
                             extra = self.set_extra(ChainUnitType.type_feature)) for (i,_) in enumerate(self.features)]
       return features

    def register_error(self, error_index):
        if error_index < len(self.feature_errors):
            self.feature_errors[error_index] += 1
            self.cummulative_error += 1

    def decrease_errors(self):
        if self.cummulative_error > 1:
            self.cummulative_error //= 2
        else:
            self.cummulative_error = 0

        for i in range(len(self.feature_errors)):
            error = self.feature_errors[i]
            if error > 1:
                self.feature_errors[i]//=2
            else:
                self.feature_errors[i] = 0
        
    
    def get_main_title(self):
        return self.entity

    def register_progress(self, is_solved = False):
        timing = self.basic_timing_per_level[self.feature_level]
        level = self.feature_level
        if is_solved:
            self.basic_timing_per_level[self.feature_level] = timing +5 if timing < 50 else 50 
            self.feature_level = level + 1 if level < 2 else 2 
            self.rised = True
            self.decreased = False
        else:
            self.basic_timing_per_level[self.feature_level] = timing -5 if timing > 30 else 30 
            self.feature_level = level -1 if level > 0 else 0 
            self.decreased = True
            self.rised = False

    def select(self):
        self.rised = False
        self.decreased = False

    def deselect(self):
        self.rised = False
        self.decreased = False

    def get_features_len(self):
        return len(self.keys)

    def __repr__(self):
        return f"{self.entity} | progress = {self.feature_level} | errors = {self.cummulative_error}"


class FeaturesChain():
    def __init__(self, chain_no, features, is_review_requires = True):
        self.chain_no = chain_no
        self.features = features

        if is_review_requires:
            self.features.append(self.create_review_chain(self.features))
            self.features[-1].review = True

        self.progression_level = 0
        self.errors_mapping = [[0 for _ in range(10)] for j in range(5)]
        self.max_error = 0
        self.cummulative_error = 0
        self.fresh_errors = 0
        self.last_review_urge = 0
        self.active_position = -1
        self.ascended = False

    def create_review_chain(self, features):
        entity = str(self.chain_no).rjust(3, "0")
        review_features = []
        for feature in features:
            review_features.append(feature.entity)
        return ChainedFeature(entity, review_features)

    def ascend(self):
        for feature in self.features:
            feature.feature_level = 2
            feature.deselect()

    def set_errors(self, errors_mapping):
        self.errors_mapping = errors_mapping
        for feature, feature_errors in zip(self.features, self.errors_mapping):
            feature.feature_errors = feature_errors
            feature.cummulative_error = sum(feature_errors)
        self.max_error = max([max(feature.feature_errors, default=0) for feature in self.features], default=0)
        self.cummulative_error = sum(sum(feature.feature_errors) for feature in self.features)

    def update_errors(self, register_new = False):
        if register_new:
            self.fresh_errors += 1

        for error_index, (feature, _) in enumerate(zip(self.features, self.errors_mapping)):
            self.errors_mapping[error_index] = feature.feature_errors
        self.max_error = max([max(feature.feature_errors, default = 0) for feature in self.features], default=0)
        self.cummulative_error = sum(sum(feature.feature_errors) for feature in self.features)

    def get_worst_features(self, features_no = 1):
        sorted_by_mistake = sorted(self.features,key = lambda _ : _.cummulative_error, reverse = True)
        return sorted_by_mistake[:features_no] 


    def initialize_images(self, images_list):
        for image, feature in zip(images_list, self.features):
            feature.attached_image = image
        self.features[-1].attached_image = images_list

    def get_next_feature(self):
        level = self.features[self.active_position].feature_level
        is_fallback = self.features[self.active_position].decreased
        is_up = self.features[self.active_position].rised
        if level == 0 and is_fallback:
            return self.features[self.active_position]
        if level == 1:
            return self.features[self.active_position]
        if level == 2 and not is_up:
            return self.features[self.active_position]
        
        self.features[self.active_position].deselect()
        self.active_position += 1
        if self.active_position >= len(self.features):
            self.active_position = 0
            if self.fresh_errors <= 3:
                self.progression_level += 1
            elif self.fresh_errors <= 6:
                self.progression_level = self.progression_level
            else:
                self.progression_level -= 1
                if self.progression_level < 0:
                    self.progression_level = 0

            self.fresh_errors = 0

            return None
        self.features[self.active_position].select()
        return self.features[self.active_position]


class ChainedModel():
    def __init__(self, chains):
        self.chains = chains
        self.active_chain = None
        self.old_limit = 2
        self.new_limit = 2
        self.mistakes_trigger = False
        self.mistakes_chain = []
        self.burning_chain = []

        is_restored = self.restore_results(PROGRESSION_FILE)

        if not is_restored:
            self.active_chain = self.get_active_chain()
            self.dump_results(PROGRESSION_FILE)
        else:
            self.change_active_chain()

        self.attach_images(IMAGES_MAPPING_FILE)

    def resample(self):

        if len(self.mistakes_chain) >= 5:
            self.mistakes_trigger = True

        for chain in self.chains:
            if chain.progression_level > 0:

                chain.last_review_urge = chain.last_review_urge - 1

        if self.old_limit:
            self.chains.sort(key = lambda _ : _.progression_level + _.last_review_urge * 0.25)
        else:
            self.chains.sort(key = lambda _ : _.progression_level)
            if not self.new_limit:

                self.old_limit = 2
                self.new_limit = 2
        self.dump_results(PROGRESSION_FILE)

    def add_mistake_chains(self):

        if not self.active_chain:
            return

        worst_features = self.active_chain.get_worst_features(features_no = 2)

        for feature in worst_features:
            if feature.cummulative_error == 0 or feature in self.mistakes_chain:
                continue
            self.mistakes_chain.append(feature)

        self.mistakes_chain.sort(key = lambda _ : _.cummulative_error, reverse = True)

    def change_active_chain(self):

        self.add_mistake_chains()

        self.resample()


        if self.mistakes_trigger:
            self.mistakes_trigger = False

            if len(self.mistakes_chain) > 5:
                mistakes_to_work, self.mistakes_chain = self.mistakes_chain[:5], self.mistakes_chain[5:]

                for mistake in mistakes_to_work:
                    mistake.decrease_errors()
                self.active_chain =  FeaturesChain(-1, mistakes_to_work, is_review_requires = False)
                return

        self.active_chain = self.chains[0]

        if self.active_chain.last_review_urge < 0:
            self.old_limit -= 1
        else:
            self.new_limit -= 1

        self.active_chain.last_review_urge = 0
        self.active_chain.update_errors()

    def get_options_list(self, sample):
        options = [sample.text]
        while len(options) < 6:
            try:
                random_features_chain = random.choice
                random_chain = random.choice(random.choice(self.chains).features)
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

    def get_next_feature(self):
        next_feature = self.active_chain.get_next_feature()
        if not next_feature:
            self.change_active_chain()
            next_feature = self.active_chain.get_next_feature()

        if not next_feature.review and not next_feature in self.burning_chain:
            self.burning_chain.append(next_feature)
            print(self.burning_chain)

        return next_feature

    def is_burning(self):
        return len(self.burning_chain) >= 30

    def get_burning_features_list(self):
        features_list = []
        self.burning_chain = random.sample(self.burning_chain, 30)
        for feature in self.burning_chain:
            features_list.append([feature.entity])
            features_list[-1] += [feature.features[0]]
        self.burning_chain = []
        return features_list

    def dump_results(self, progression_file):
        backup = {}
        for chain in self.chains:
            backup[chain.chain_no] = [chain.progression_level, chain.last_review_urge, chain.errors_mapping]
        with open(progression_file, "w") as current_progress:
            json.dump(backup, current_progress, indent=2)

    def attach_images(self, images_file):
        if os.path.exists(images_file):
            images = {}
            with open(images_file) as images_ordered:
                images = json.load(images_ordered)
            if images:
                for chain in self.chains:
                    if chain.chain_no in images:
                        chain.initialize_images(images[chain.chain_no])
                    else:
                        print(f"Chain {chain.chain_no} have no image prepared")

    def restore_results(self, progression_file):
        if os.path.exists(progression_file):
            progress = {}
            with open(progression_file) as saved_prgress:
                progress = json.load(saved_prgress)
            if progress:
                for chain in self.chains:
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

    def get_chains_progression(self):
        minimal_level = min(self.chains, key = lambda _ : _.progression_level).progression_level
        mastered = len(list(filter(lambda _: _.progression_level > minimal_level, self.chains)))
        return f"{minimal_level}x {mastered}/{len(self.chains)}"


    def get_active_chain(self):

        return self.active_chain
