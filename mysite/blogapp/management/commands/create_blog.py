from typing import Sequence

from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Author, Category,Tag, Article


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create Article")
        author = Author.objects.get(name="Pushkin")
        category = Category.objects.get(name="A masterpiece")
        tags: Sequence[Tag] = Tag.objects.only("id").all()
        article, created = Article.objects.get_or_create(
            title="Телега жизни",
            content="Хоть тяжело подчас в ней бремя,\n"
                    "Телега на ходу легка;\n"
                    "Ямщик лихой, седое время,\n"
                    "Везет, не слезет с облучка.",
            author=author,
            category=category,
        )
        for tag in tags:
            article.tags.add(tag)
        article.save()
        self.stdout.write(f"Create article {article}")
