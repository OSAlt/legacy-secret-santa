from incf.countryutils import transformations

class Person:
    def __init__(self, name, email, invalid_matches, amazon, country):
        self.name = name
        self.email = email
        self.invalid_matches = invalid_matches
        self.amazon = amazon
        try:
            self.continent = transformations.cn_to_ctn(country)
        except KeyError as e:
            self.continent = transformations.cn_to_ctn(self.__handle_country_name(country))

    # Some names in ISO 3166 are almost impossible to get right. So lets help
    # our users out a little bit by matching some common ones.
    def __handle_country_name(self, country):
        for long_name in ["United States of America",
                          "United Kingdom of Great Britain & Northern Ireland"]:
            if long_name.find(country) != -1:
                return long_name
        raise KeyError(country)

    def amazon_url(self):
        return self.amazon

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)
