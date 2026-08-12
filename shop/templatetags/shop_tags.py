from django import template
from shop.models import Category, Like

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.all()

@register.simple_tag()
def get_likes(user):
    likes = Like.objects.filter(user=user)
    return [like.product for like in likes]