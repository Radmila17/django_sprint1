"""Приложение blog.

Нужно для вывода главной страницы, информации о каждом посте,
а также для вывода всех постов определенных категорий.
"""

from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('edit_profile/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('<slug:slug>/', views.ProfilePostsListView.as_view(), name='profile'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:id>', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<post_id>/delete_comment/<comment_id>/', views.delete_comment, name='delete_comment'),
]
