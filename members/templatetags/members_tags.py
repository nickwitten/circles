from django import template

register = template.Library()

@register.filter
def get_obj_attr(obj, attr):
    if attr == None or attr == '':
        return ''
    else:
        result = getattr(obj, attr)
        if result == None:
            return 'Not Available'
        return result
