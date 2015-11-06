import datetime
from django import template

register = template.Library()

@register.simple_tag
def get_current_index(inner_counter, outer_counter, tags_per_row):
    return inner_counter + (outer_counter * tags_per_row)


