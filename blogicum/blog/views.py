from typing import List, Dict, Union

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Post, Category


def add_filters(func):
    def wrapper(*args, **kwargs):
        current_time = timezone.now()
        filters = {
            'pub_date__lte': current_time,
            'is_published': True,
            'category__is_published': True
        }
        kwargs['filters'] = filters
        kwargs['current_time'] = current_time
        return func(*args, **kwargs)
    return wrapper


@add_filters
def get_post_list(category_slug=None, filters=None, current_time=None):
    if category_slug:
        filters['category__slug'] = category_slug

    return Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        **filters
    )


def index(request):
    template = 'blog/index.html'
    post_list = get_post_list().order_by('-pub_date')[:5]
    context = {'post_list': post_list}
    return render(request, template, context)


@add_filters
def post_detail(request, post_id, filters=None, current_time=None):
    template = 'blog/detail.html'

    post = get_object_or_404(Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(**filters), pk=post_id)

    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.only(
            'title', 'description'
        ).filter(slug=category_slug, is_published=True)
    )

    post_list = get_post_list(category_slug=category_slug)

    context = {
        'post_list': post_list,
        'category': category
    }
    return render(request, template, context)
