# Standard Library
import calendar
from datetime import datetime

# Django
from django.template.defaulttags import register


@register.filter(name="current_month")
def current_month(value):
    try:
        month_number = int(value)
        return calendar.month_name[month_number]
    except (ValueError, TypeError, IndexError):
        return datetime.now().strftime("%B")
