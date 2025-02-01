from django import template

register = template.Library()

@register.filter
def seconds_to_minutes(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s" if remaining_seconds else f"{minutes}m"

