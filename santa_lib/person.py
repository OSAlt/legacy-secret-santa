import re
from incf.countryutils import transformations


class Person:
    @classmethod
    def construct_email_recipient(cls, raw_string):
        obj = cls()
        name, email = re.match(r'([^<]*)<([^>]*)>', raw_string).groups()
        obj.name = name.strip()
        obj.email = email
        obj.continent = None

        return obj


    @classmethod
    def construct_santa_recipient(cls, raw_string):
        obj = cls()
        name, email, amazon, country = re.match(r'([^<]*)<([^>]*)>.*(http[^ ]*) ([^<]+)', raw_string).groups()
        obj.name = name.strip()
        obj.email = email
        obj.invalid_matches = []
        obj.amazon = amazon
        try:
            obj.continent = transformations.cn_to_ctn(country)
            obj.country = country
        except KeyError as e:
            obj.continent = transformations.cn_to_ctn(obj.__handle_country_name(country))

        return obj

    # Some names in ISO 3166 are almost impossible to get right. So lets help
    # our users out a little bit by matching some common ones.
    @staticmethod
    def __handle_country_name(country):
        for long_name in ["United States of America",
                          "United Kingdom of Great Britain & Northern Ireland"]:
            if long_name.find(country) != -1:
                return long_name
        raise KeyError(country)

    def amazon_url(self):
        return self.amazon

    def __str__(self):
        return "%s <%s> %s" % (self.name, self.email, self.continent)
