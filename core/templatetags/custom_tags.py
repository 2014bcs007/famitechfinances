# search.templatetags.class_name.py
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter()
def class_name(value):
    return value.__class__.__name__

@register.filter()
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)
@register.filter()
def get_value(dictionary,key):
    print(dictionary.values())
    return key
@register.filter()
def currency(amount):
    if not amount:
        return amount
    try:
        amount = float(round(float(amount), 2))
        return "%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])
    except Exception as ex:
        return amount
        print(ex)


@register.filter()
def concat(value1, value2):
    return str(value1) + str(value2)