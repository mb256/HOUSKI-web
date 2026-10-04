from django import template

register = template.Library()


@register.filter
def exclude_param(querydict, key):
    """Return a copy of `querydict` with `key` removed, so pagination links
    can preserve other GET params (e.g. ?category=) while overriding `page`.
    """
    qd = querydict.copy()
    qd.pop(key, None)
    return qd
