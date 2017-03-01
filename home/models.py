from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class HomePage(Page):
    body = RichTextField(max_length=250, blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    def __str__(self):
        return "Homepage"
