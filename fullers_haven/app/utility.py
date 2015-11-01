from time import strptime
from django.utils.datetime_safe import strftime

class GlobalOperations(object):
    @staticmethod
    def get_date_as_text(date, include_time):
        if date:
            format = "%d %b %Y"
            
            if include_time:
                format = "{0}{1}".format(format, ", %I:%M %p")

            return date.strftime(format)
        else:
            return "N/A"

class Anonymous(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)



