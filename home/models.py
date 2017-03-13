from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from blog.models import BlogPage


class HomePage(Page):
    body = RichTextField(max_length=500, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    def __str__(self):
        return "Homepage"

    def get_context(self, request):
        # get list of blog pages
        blogpages = BlogPage.objects.live().order_by(
            '-first_published_at')
        # get just the first four to show as most recent
        blogpages = blogpages[:3]
        #update page context with blogpages
        context = super(HomePage, self).get_context(request)
        context['blogpages'] = blogpages
        return context

