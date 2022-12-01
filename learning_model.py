import random

class MarkedAlias():
    def __init__(self, content, key, attached_unit, active = False):
        self.content = content
        self.content_type = "text"
        self.active = active
        self.correct = False
        self.wrong = False
        self.attached_unit = attached_unit
        self.key = key

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def register_match(self):
        self.attached_unit.deactivate(positive_feedback = True)

    def register_error(self):
        self.attached_unit.deactivate(positive_feedback = False)

class SemanticUnit():
    def __init__(self, aliases):
        self.aliases = aliases
        self.activated = False
        self.learning_score = 100 
        self.key = id(self)

    def __increment(self):
        self.learning_score += 1
            

    def __decrement(self):
        self.learning_score -= 1 
        if self.learning_score <= 98:
            self.learning_score = 98

    def activate(self):
        self.activated = True

    def produce_pair(self):
        if not self.activated:
            return [MarkedAlias(_, self.key, self) for _ in random.sample(self.aliases, 2)]
        else:
            selected = [MarkedAlias(_, self.key, self) for _ in random.sample(self.aliases, 2)]
            active = random.choice(selected)
            active.activate()
            
            return selected

    def deactivate(self, positive_feedback = False):
        if self.activated:

            if positive_feedback:
                self.__increment()
            else:
                self.__decrement()

        self.activated = False

class ChainUnitType():
    type_key = "type_key"
    type_feature = "type_feature"
    mode_open =  "mode_open"
    mode_question =  "mode_question"
    mode_active_question = "mode_active_question"
    mode_hidden = "mode_hidden"
    mode_highligted = "mode_highligted"
    position_subtitle = "position_subtitle"
    position_features = "position_features"
    position_keys = "position_keys"
    font_cyrillic = "font_cyrillic"
    font_utf = "font_utf"

class ChainUnit():
    def __init__(self,
                 text,
                 type = None,
                 mode = None,
                 position = None,
                 order_no = None,
                 font = ChainUnitType.font_utf):

        self.text = text
        self.type = type
        self.mode = mode
        self.position = position
        self.order_no = order_no
        self.font = font

class ChainedFeature():
    def __init__(self, entity, in_key, out_key, main_feature, key_feature_pairs): 
        self.entity = entity
        self.in_key = in_key.upper()
        self.out_key = out_key.upper()
        self.main_feature = main_feature
        self.keys = [_.upper() for _ in key_feature_pairs[0::2]]
        self.features = key_feature_pairs[1::2]
        self.progression_level = 0
        self.decreased = False
        self.rised = False
        self.basic_timing_per_level = {0:20,
                                       1:40,
                                       2:40,
                                       3:40,
                                       4:40,
                                       5:40}

    def set_mode(self, unit_type):
        if self.progression_level == 0:
            return ChainUnitType.mode_open
        elif self.progression_level == 1 and unit_type == ChainUnitType.type_key:
            return ChainUnitType.mode_question 
        elif self.progression_level == 2 and unit_type == ChainUnitType.type_feature:
            return ChainUnitType.mode_question
        elif self.progression_level == 3 and unit_type == ChainUnitType.type_feature:
            return ChainUnitType.mode_question
        elif self.progression_level == 3 and unit_type == ChainUnitType.type_key:
            return ChainUnitType.mode_hidden
        else:
            return ChainUnitType.mode_open

    def get_timing(self):
        return self.basic_timing_per_level[self.progression_level]


    def get_context(self):
       keys = [ChainUnit(_, ChainUnitType.type_key,
                         self.set_mode(ChainUnitType.type_key),
                         ChainUnitType.position_keys, i+1,
                         font=ChainUnitType.font_cyrillic) for (i,_) in enumerate(self.keys)] 
       features = [ChainUnit(_, ChainUnitType.type_feature,
                                 self.set_mode(ChainUnitType.type_feature),
                                 ChainUnitType.position_features, i+1) for (i,_) in enumerate(self.features)]
       subtitle = [ChainUnit(self.in_key, ChainUnitType.type_key,
                                 self.set_mode(ChainUnitType.type_key),
                                 ChainUnitType.position_keys, 0,
                                 font = ChainUnitType.font_cyrillic)]
       subtitle += [ChainUnit(self.main_feature, ChainUnitType.type_feature,
                                 self.set_mode(ChainUnitType.type_feature),
                                 ChainUnitType.position_keys, 0)]
       return keys + features + subtitle


    def get_main_title(self):
        return self.entity

    def register_progress(self, is_solved = False):
        timing = self.basic_timing_per_level[self.progression_level]
        level = self.progression_level
        if is_solved:
            self.basic_timing_per_level[self.progression_level] = timing +5 if timing < 50 else 50 
            self.progression_level = level + 1 if level < 4 else 4 
            self.rised = True
            self.decreased = False
        else:
            self.basic_timing_per_level[self.progression_level] = timing -5 if timing > 20 else 20 
            self.progression_level = level -1 if level > 0 else 0 
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


class FeaturesChain():
    def __init__(self, chain_no, features):
        self.chain_no = chain_no
        self.features = features
        self.progression_level = 0
        self.active_position = -1

    def get_next_feature(self):
        # 0 level - card readed.
        # Next step is to restore associated keys
        level = self.features[self.active_position].progression_level
        is_fallback = self.features[self.active_position].decreased
        is_up = self.features[self.active_position].rised
        # two main factors are card chain level and
        # the way level was acheived - by recall or by forgetting some
        if level == 0 and is_fallback:
            # back to zero means - learn chain again
            return self.features[self.active_position]
        if level == 1:
            # reached 1 means - learn keys
            return self.features[self.active_position]
        if level == 2:
            return self.features[self.active_position]
        if level == 3:
            return self.features[self.active_position]
        if level == 4 and not is_up:
            return self.features[self.active_position]
        
        self.features[self.active_position].deselect()
        self.active_position += 1
        if self.active_position >= len(self.features):
            self.active_position = 0
        self.features[self.active_position].select()
        return self.features[self.active_position]

    def get_options_list(self, sample):
        options = [sample.text]
        for i in range(5):
            random_chain = random.choice(self.features)
            if sample.type == ChainUnitType.type_key:
                selected = random.choice(random_chain.keys)
                options.append(selected)
            if sample.type == ChainUnitType.type_feature:
                selected = random.choice(random_chain.features)
                options.append(selected)
        random.shuffle(options)
        return options

    def get_features_list(self):
        units_list = [ChainUnit(_.entity + f" {_.progression_level}", font = ChainUnitType.font_utf) for _ in self.features]
        # TODO specify in config
        if len(units_list) < 12:
            delta_len = 12 - len(units_list)
            units_list += [ChainUnit("") for _ in range(delta_len)]
        elif len(units_list) > 12:
            units_list = units_list[:12]
        return units_list



class ChainedModel():
    def __init__(self, chains):
        self.chains = chains
        self.active_chain = self.set_active_chain() 

    def resample(self):
        self.chains.sort(key = lambda _ : _.progression_level)

    def get_chains_list(self):
        units_list = [ChainUnit(_.features[0].entity + "..." + _.features[-1].entity + f" {_.progression_level}", font = ChainUnitType.font_utf) for _ in self.chains]
        # TODO specify in config
        if len(units_list) < 12:
            delta_len = 12 - len(units_list)
            units_list += [ChainUnit("") for _ in range(delta_len)]
        elif len(units_list) > 12:
            units_list = units_list[:12]
        return units_list

    def set_active_chain(self):
        return self.chains[0]

    def get_active_chain(self):
        return self.active_chain
