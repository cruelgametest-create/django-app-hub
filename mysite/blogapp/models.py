from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """
    Модель Author представляет автора статьи.
    """
    class Meta:
        ordering = ["name"]
        verbose_name = _("Author")

    """ name — имя автора. """
    name = models.CharField(max_length=100, db_index=True)
    """ bio — биография автора. """
    bio = models.TextField(null=False, blank=True, db_index=True)


class Category(models.Model):
    """
    Модель Category представляет категорию статьи.
    """
    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")

    """ name — название категории. """
    name  = models.CharField(max_length=40, db_index=True)


class Tag(models.Model):
    """
    Модель Tag представляет тэг, который можно назначить статье.
    """
    class Meta:
        ordering = ["name"]
        verbose_name = _("Tag")

    """ name — название тэга. """
    name  = models.CharField(max_length=20, db_index=True)


class Article(models.Model):
    """
    Модель Article представляет статью.
    """
    class Meta:
        # ordering = ["pub_date"]
        verbose_name = _("Article")

    """ title — заголовок статьи. """
    title  = models.CharField(max_length=200, db_index=True)
    """ content — содержимое статьи. """
    content = models.TextField(null=True, blank=True, db_index=True)
    """ pub_date — дата публикации статьи. """
    pub_date = models.DateTimeField(null=True, blank=True)
    """ author — автор статьи. """
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    """ category — категория статьи. """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    """ tags — тэги статьи. """
    tags = models.ManyToManyField(Tag, related_name="articles", null=True, blank=True)

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})
