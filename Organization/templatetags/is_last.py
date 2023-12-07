
import datetime
from datetime import datetime
from django import template

register = template.Library()

@register.filter(name='isLast')
def isLast(value, count ):
    if(int(value) == int(count)):
        return "True"
    else:
        return "False"
