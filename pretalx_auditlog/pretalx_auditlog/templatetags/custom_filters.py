from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Returns the value for the given key in the dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None  # Return None if the key doesn't exist
