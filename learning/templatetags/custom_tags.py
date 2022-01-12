from django import template
import random

register = template.Library()


@register.filter()
def myShuffle(mylist):
    return random.shuffle(mylist)
