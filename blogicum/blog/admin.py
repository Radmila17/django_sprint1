from django.contrib import admin
from .models import Post, Category, Location

admin.site.register(Location)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'is_published', 'created_at')
    list_editable = ('is_published',)


class PostInLine(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_editable = ('is_published',)
    inlines = (PostInLine,)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
