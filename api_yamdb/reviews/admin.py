from django.contrib import admin

from .models import Category, Genre, Title, Review, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'description')
    search_fields = ('name', 'description', 'category__name', 'genre__name')
    list_filter = ('category', 'genre')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'text', 'score', 'pub_date')
    search_fields = ('author__username', 'title__name', 'text')
    list_filter = ('author', 'title', 'pub_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review', 'text', 'pub_date')
    search_fields = ('author__username', 'review__title__name', 'text')
    list_filter = ('author', 'review', 'pub_date')
