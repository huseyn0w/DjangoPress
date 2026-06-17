from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import sanitize_html, unique_slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class Status(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")


class Category(TimeStampedModel):
    """Hierarchical taxonomy term (a category can have a parent category)."""

    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=100, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = unique_slugify(self, self.name, max_length=100)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("content:category", args=[self.slug])


class Tag(TimeStampedModel):
    name = models.CharField(_("name"), max_length=50)
    slug = models.SlugField(_("slug"), max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = unique_slugify(self, self.name, max_length=50)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("content:tag", args=[self.slug])


class PublishableQuerySet(models.QuerySet):
    def published(self) -> models.QuerySet:
        return self.filter(status=Status.PUBLISHED, published_at__lte=timezone.now())

    def drafts(self) -> models.QuerySet:
        return self.filter(status=Status.DRAFT)


class Post(TimeStampedModel):
    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    excerpt = models.TextField(_("excerpt"), blank=True)
    body = models.TextField(_("body"), blank=True)
    featured_image = models.ImageField(
        _("featured image"), upload_to="posts/", blank=True, null=True
    )
    status = models.CharField(
        _("status"), max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    categories = models.ManyToManyField(
        Category, verbose_name=_("categories"), blank=True, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, verbose_name=_("tags"), blank=True, related_name="posts")

    objects = PublishableQuerySet.as_manager()

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        # nulls_last so unpublished (NULL published_at) posts sort after live ones,
        # including in the Django admin list under PostgreSQL.
        ordering = [models.F("published_at").desc(nulls_last=True), "-created_at"]
        permissions = [("publish_post", "Can publish posts")]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = unique_slugify(self, self.title, max_length=200)
        # Sanitize all author-supplied HTML server-side, every save.
        self.body = sanitize_html(self.body)
        self.excerpt = sanitize_html(self.excerpt)
        # Stamp publish time on first publish only. Re-publishing after an unpublish
        # deliberately keeps the original date so permalinks/feeds stay stable.
        if self.status == Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("content:post_detail", args=[self.slug])

    @property
    def is_published(self) -> bool:
        return self.status == Status.PUBLISHED and bool(
            self.published_at and self.published_at <= timezone.now()
        )

    def can_be_viewed_by(self, user) -> bool:
        """Who may see this post via its public URL.

        Published posts are public. Drafts are visible only to their author and to
        content managers — those who can delete any post (Editors/Admins). Authors
        and Contributors therefore see their own drafts but never each other's.
        """
        if self.is_published:
            return True
        if not user.is_authenticated:
            return False
        return user == self.author or user.has_perm("content.delete_post")


class Page(TimeStampedModel):
    """A standalone, optionally hierarchical page (About, Contact, ...)."""

    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="pages",
    )
    body = models.TextField(_("body"), blank=True)
    template = models.CharField(_("template"), max_length=100, default="default")
    status = models.CharField(
        _("status"), max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    objects = PublishableQuerySet.as_manager()

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = unique_slugify(self, self.title, max_length=200)
        self.body = sanitize_html(self.body)
        if self.status == Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("content:page_detail", args=[self.slug])

    @property
    def is_published(self) -> bool:
        return self.status == Status.PUBLISHED and bool(
            self.published_at and self.published_at <= timezone.now()
        )

    def can_be_viewed_by(self, user) -> bool:
        """Published pages are public; drafts only to users who can edit pages."""
        if self.is_published:
            return True
        return user.is_authenticated and user.has_perm("content.change_page")


class Revision(TimeStampedModel):
    """Immutable snapshot of a post/page body taken on each save."""

    title = models.CharField(_("title"), max_length=200)
    body = models.TextField(_("body"), blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} @ {self.created_at:%Y-%m-%d %H:%M}"


class PostRevision(Revision):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="revisions")


class PageRevision(Revision):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="revisions")
