from django import template
from core.models import LyfeUser

register = template.Library()

@register.filter(name='user_greeting_name')
def user_greeting_name(value):
    """Generate a name to be used for greeting a user"""
    if value.first_name is not None and value.first_name != '':
        return value.first_name
    else:
        return value.username

@register.filter(name='user_avatar_url')
def user_avatar_url(username):
    """Returns URL of user's avatar"""
    try:
        user = LyfeUser.objects.get(pk = username)
        return user.avatar.url
    except LyfeUser.DoesNotExist:
        print "LyfeUser doesn't exist"
        return