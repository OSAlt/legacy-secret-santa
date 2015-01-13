class Person:
    def __init__(self, name, email, invalid_matches, amazon):
        self.name = name
        self.email = email
        self.invalid_matches = invalid_matches
        self.amazon = amazon

    def amazon_url(self):
        return self.amazon

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)
