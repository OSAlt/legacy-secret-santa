class Pair:
    def __init__(self, giver, receiver):
        self.giver = giver
        self.receiver = receiver

    def __str__(self):
        return "%s (%s) ---> %s (%s)" % (self.giver.name, self.giver.continent, self.receiver.name, self.receiver.continent)