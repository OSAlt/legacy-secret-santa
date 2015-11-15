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

    def __handle_country_name(country):
        return "United States of America"

    def amazon_url(self):
        return self.amazon

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)
