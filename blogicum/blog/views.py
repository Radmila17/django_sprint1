from typing import Any
# from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.db.models import Count
# from django.http import HttpRequest, Http404, HttpResponse
from blog.models import Post, Category, User, Comment
from datetime import datetime
from django.shortcuts import get_list_or_404, redirect, render
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from .forms import PostCreateForm, CommentForm, ProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import pytz


posts_queryset = Post.objects.select_related('location', 'author', 'category')
categories_queryset = Category.objects.all()
comments_queryset = Comment.objects.select_related('post')
posts_with_comment_count = posts_queryset.annotate(
    comment_count=Count('comments')
)


def index(request):
    """Homepage."""
    template_name = 'blog/index.html'
    posts = get_list_or_404(posts_with_comment_count.filter(
        pub_date__lt=datetime.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-id'))
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }

    return render(request, template_name, context)


def post_detail(request, id):
    """One post's information."""
    template_name = 'blog/detail.html'
    form = CommentForm()
    post_by_id = get_object_or_404(
        posts_queryset, pk=id
    )
    if request.user != post_by_id.author and (
        post_by_id.pub_date > datetime.now().replace(tzinfo=pytz.utc) or
        post_by_id.is_published is False
    ):
        return render(request, 'blog/delayed_post.html')
    else:
        context = {
            'form': form,
            'post': post_by_id,
            'comments': post_by_id.comments.all(),
        }
        return render(request, template_name, context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post_id)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'id'
    form_class = CommentForm
    login_url = 'login'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        post = get_object_or_404(Post.objects.filter(
            id=self.kwargs['post_id']
        ))
        queryset = post.comments.all()
        return queryset

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])


def category_posts(request, category_slug):
    """List with posts by category."""
    template_name = 'blog/category.html'
    posts_by_category = posts_with_comment_count.filter(
        is_published=True,
        pub_date__lt=datetime.now(),
        category__slug=category_slug,
    )
    category_of_posts = get_object_or_404(
        categories_queryset.filter(slug=category_slug), is_published=True,
    )
    paginator = Paginator(posts_by_category, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category_of_posts,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostCreateForm
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        profile_name = self.request.user.username
        return reverse_lazy('blog:profile', args=[profile_name])


class PostUpdateView(UpdateView):
    template_name = 'blog/create.html'
    model = Post
    pk_url_kwarg = 'id'
    form_class = PostCreateForm

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Post, pk=self.kwargs['id'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs) 

    def get_success_url(self):
        post_id = self.kwargs['id']
        return reverse_lazy('blog:post_detail', args=[post_id])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        profile_name = self.request.user.username
        return reverse_lazy('blog:profile', args=[profile_name])


class ProfilePostsListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    ordering = 'title'
    paginate_by = 10

    def get_queryset(self, **kwargs) -> QuerySet[Any]:
        author = get_object_or_404(
            User.objects.filter(username=self.kwargs['slug'])
        )
        if self.request.user == author:
            queryset = posts_with_comment_count.filter(
                author__username=self.kwargs['slug']
            )
        else:
            queryset = posts_with_comment_count.filter(
                is_published='True',
                pub_date__lt=datetime.now().replace(tzinfo=pytz.utc),
                author__username=self.kwargs['slug'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(
            User.objects.filter(username=self.kwargs['slug'])
        )
        context['profile'] = author
        return context


# class PostDeleteView(DeleteView):
#     model = Post
#     slug_field = 'id'
#     slug_url_kwarg = 'post_id'
#     success_url = reverse_lazy('blog:index')

#     def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
#         get_object_or_404(posts_query_set, id=self.kwargs['post_id'], author__id=self.request.user.id)
#         return super().dispatch(request, *args, **kwargs)

#     def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
#         queryset = posts_query_set.filter(id=self.kwargs['post_id'])
#         return super().get_object(queryset)


def delete_post(request, post_id):
    post = get_object_or_404(
        posts_queryset,
        id=post_id,
        author=request.user
    )
    form = PostCreateForm(instance=post)
    context = {
        'post': post,
        'form': form,
    }
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', slug=request.user.username)
    return render(request, 'blog/post_confirm_delete.html', context)


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        comments_queryset,
        post__id=post_id,
        id=comment_id
    )
    form = CommentForm(instance=comment)
    post = get_object_or_404(
        posts_queryset,
        id=post_id,
    )
    context = {
        'form': form,
        'post': post,
        'comment': comment,
    }
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment_confirm_delete.html', context)
