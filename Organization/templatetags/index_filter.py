
import datetime
from datetime import datetime
from django import template

register = template.Library()

@register.filter(name='index')
def index(value, lst ):
    pass
    # if(lst[int(i)] in ["createdAt" , "updatedAt"]):
    #     return formats.date_format( value, "DATETIME_FORMAT")
