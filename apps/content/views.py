from __future__ import annotations

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Page, Post, Service, Tag


class PublishedPostMixin:
    """Restrict post querysets to published items for the public site."""

    paginate_by = 10

    def get_queryset(self) -> QuerySet:
        return (
            Post.objects.published().select_related("author").prefetch_related("categories", "tags")
        )


class PostListView(PublishedPostMixin, ListView):
    template_name = "content/post_list.html"
    context_object_name = "posts"


class CategoryPostListView(PublishedPostMixin, ListView):
    template_name = "content/post_list.html"
    context_object_name = "posts"

    def get_queryset(self) -> QuerySet:
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return super().get_queryset().filter(categories=self.category)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["taxonomy"] = self.category
        return ctx


class TagPostListView(PublishedPostMixin, ListView):
    template_name = "content/post_list.html"
    context_object_name = "posts"

    def get_queryset(self) -> QuerySet:
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return super().get_queryset().filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["taxonomy"] = self.tag
        return ctx


class PostDetailView(DetailView):
    template_name = "content/post_detail.html"
    context_object_name = "post"
    queryset = Post.objects.select_related("author").prefetch_related("categories", "tags")

    def get_object(self, queryset: QuerySet | None = None) -> Post:
        # Resolve from all posts, then apply the object-level visibility rule so
        # draft ownership is enforced (a Contributor can't read others' drafts).
        post = super().get_object(queryset)
        if not post.can_be_viewed_by(self.request.user):
            raise Http404
        return post


class PageDetailView(DetailView):
    template_name = "content/page_detail.html"
    context_object_name = "page"
    queryset = Page.objects.all()

    def get_object(self, queryset: QuerySet | None = None) -> Page:
        page = super().get_object(queryset)
        if not page.can_be_viewed_by(self.request.user):
            raise Http404
        return page


class ServiceListView(ListView):
    template_name = "content/service_list.html"
    context_object_name = "services"

    def get_queryset(self) -> QuerySet:
        return Service.objects.published()


class ServiceDetailView(DetailView):
    template_name = "content/service_detail.html"
    context_object_name = "service"
    queryset = Service.objects.all()

    def get_object(self, queryset: QuerySet | None = None) -> Service:
        service = super().get_object(queryset)
        if not service.can_be_viewed_by(self.request.user):
            raise Http404
        return service
