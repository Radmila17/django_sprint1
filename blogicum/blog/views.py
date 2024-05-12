from django.shortcuts import render
from blog.models import Post, Category
from datetime import datetime
from django.shortcuts import get_object_or_404

posts_query_set = Post.objects.select_related('location', 'author', 'category')
categories_query_set = Category.objects.all()


def index(request):
    template_name = 'blog/index.html'
    posts = posts_query_set.filter(
        pub_date__lt=datetime.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-id')[0:5]
    context = {'post_list': posts}
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'
    post_by_id = get_object_or_404(
        posts_query_set.filter(
            pub_date__lt=datetime.now(),
            is_published=True,
            category__is_published=True,
        ), pk=id
    )

    context = {'post': post_by_id}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    posts_by_category = posts_query_set.filter(
        is_published=True,
        pub_date__lt=datetime.now(),
        category__slug=category_slug,
    )
    category_of_posts = get_object_or_404(
        categories_query_set.filter(slug=category_slug), is_published=True,
    )

    context = {
        'post_list': posts_by_category,
        'category': category_of_posts,
    }
    return render(request, template_name, context)
