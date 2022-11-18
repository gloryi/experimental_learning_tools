import random

class MarkedAlias():
    def __init__(self, content, key, active = False):
        self.content = content
        self.content_type = "text"
        self.active = active
        self.key = key

    def activate(self):
        self.active = True

class SemanticUnit():
    def __init__(self, aliases):
        self.aliases = aliases
        self.activated = False
        #self.active_alias = None
        #self.inactive_aliases = []
        self.__learning_score = 1.0
        self.key = id(self)

    def __increment(self):
        self.__learning_score *= 1.1

    def __decrement(self):
        self.__learning_score *= 0.9

    def activate(self):
        self.activated = True
        #self.active_alias = random.choice(self.aliases)

        #filter_others = lambda _ : _ != self.active_alias
        #self.inactive_aliases = list(filter(filter_others, self.aliases))

    def produce_pair(self):
        if not self.activated:
            return [MarkedAlias(_, self.key) for _ in random.sample(self.aliases, 2)]
        else:
            selected = [MarkedAlias(_, self.key) for _ in random.sample(self.aliases, 2)]
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



