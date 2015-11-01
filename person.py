from incf.countryutils import transformations

class Person:
    def __init__(self, name, email, invalid_matches, amazon, country):
        self.name = name
        self.email = email
        self.invalid_matches = invalid_matches
        self.amazon = amazon
        self.country = transformations.cc_to_cn(country)

    def amazon_url(self):
        return self.amazon

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)
