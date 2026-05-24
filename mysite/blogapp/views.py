from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Article


class ArticlesListView(ListView):
    queryset = (
        Article.objects
        .defer("content")
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-pub_date")
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and additions blog articles"
    link = reverse_lazy("blogapp:articles_list")

    def items(self):
        return (
            Article.objects
            .defer("content")
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-pub_date")[:3]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:250]
