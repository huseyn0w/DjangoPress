from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("blog/", views.PostListView.as_view(), name="post_list"),
    path("blog/category/<slug:slug>/", views.CategoryPostListView.as_view(), name="category"),
    path("blog/tag/<slug:slug>/", views.TagPostListView.as_view(), name="tag"),
    path("blog/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("pages/<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
]
