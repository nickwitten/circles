from django import template

register = template.Library()

@register.filter
def get_obj_attr(obj, attr):
    if attr == None or attr == '':
        return ''
    else:
        result = getattr(obj, attr)
        if result == None:
            return ''
        return result

@register.filter
def hash_dict(form, name):
    return form[name]

@register.filter
def field_to_label(field):
    words = field.split('_')
    try:
        words[0] = words[0][0].upper() + words[0][1:]
    except:
        words[0] = words[0].capital()
    return ' '.join(words) + ':'