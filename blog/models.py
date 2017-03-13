from django import forms
from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.fields import ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailadmin.edit_handlers import InlinePanel
from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from wagtail.wagtailsearch import index

# Create your models here.


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=32)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


class BlogIndexPage(Page):
    subtitle = "Just a dummy subtitle"
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full')
    ]

    def get_context(self, request):
        # set subtitle based on pages requested
        tag = request.GET.get('tag')
        category = request.GET.get('category')
        if tag:
            self.subtitle = "All blog pages tagged by the author: '{0}'".format(tag)
            blogpages = BlogPage.objects.live().order_by(
                '-first_published_at').filter(tags__name=tag)
        elif category:
            self.subtitle = "All blog pages in category: '{0}'".format(
                category)
            blogpages = BlogPage.objects.live().order_by(
                '-first_published_at').filter(categories__name=category)
        else:
            self.subtitle = "Showing all blog pages"
            blogpages = self.get_children().live().order_by(
                'first_published_at')

        categories = BlogCategory.objects.all()

        # now update context with reference to blog pages
        context = super(BlogIndexPage, self).get_context(request)
        context['subtitle'] = self.subtitle
        context['blogpages'] = blogpages
        context['categories'] = categories
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items')


class BlogPage(Page):
    date = models.DateField("Post Date")
    intro = models.TextField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('BlogCategory', blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog Information"),
        FieldPanel('intro'),
        FieldPanel('body', classname='full'),
        InlinePanel('gallery_images', label='Gallery Images'),
    ]

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
