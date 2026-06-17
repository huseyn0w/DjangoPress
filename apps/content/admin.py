"""Interim Django admin for content.

This is developer-facing CRUD so content is editable before the bespoke,
WordPress-style admin panel lands in Phase 5. Kept deliberately minimal.
"""

from django.contrib import admin

from .models import Category, Page, PageRevision, Post, PostRevision, Tag


class PostRevisionInline(admin.TabularInline):
    model = PostRevision
    extra = 0
    can_delete = False
    readonly_fields = ("title", "body", "author", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "updated_at")
    list_filter = ("status", "categories", "tags")
    search_fields = ("title", "body")
    date_hierarchy = "published_at"
    autocomplete_fields = ("categories", "tags")
    inlines = (PostRevisionInline,)


class PageRevisionInline(admin.TabularInline):
    model = PageRevision
    extra = 0
    can_delete = False
    readonly_fields = ("title", "body", "author", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "parent", "published_at")
    list_filter = ("status",)
    search_fields = ("title", "body")
    inlines = (PageRevisionInline,)
