from __future__ import absolute_import

import datetime

import django
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible

from .managers import QuestionManager, QuestionQuerySet


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class Topic(models.Model):
    """
    Generic Topics for FAQ question grouping
    """
    name = models.CharField(_('name'), max_length=150)
    meta_desc = models.TextField(_('meta desc'), blank=True, help_text=_('The SEO meta description.'))
    slug = models.SlugField(_('slug'), max_length=150)
    sort_order = models.IntegerField(_('sort order'), default=0,
        help_text=_('The order you would like the topic to be displayed.'))

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return ('faq_topic_detail', [self.slug])


@python_2_unicode_compatible
class Question(models.Model):
    HEADER = 2
    ACTIVE = 1
    INACTIVE = 0
    STATUS_CHOICES = (
        (ACTIVE,    _('Active')),
        (INACTIVE,  _('Inactive')),
        (HEADER,    _('Group Header')),
    )

    text = models.TextField(_('question'), help_text=_('The actual question itself.'))
    excerpt = models.TextField(_('excerpt'), blank=True, help_text=_('The answer excerpt text.'))
    answer = models.TextField(_('answer'), blank=True, help_text=_('The answer text.'))
    topic = models.ForeignKey(Topic, verbose_name=_('topic'), related_name='questions', on_delete=models.PROTECT)
    slug = models.SlugField(_('slug'), max_length=100)
    status = models.IntegerField(_('status'),
        choices=STATUS_CHOICES, default=INACTIVE,
        help_text=_("Only questions with their status set to 'Active' will be "
                    "displayed. Questions marked as 'Group Header' are treated "
                    "as such by views and templates that are set up to use them."))

    protected = models.BooleanField(_('is protected'), default=False,
        help_text=_("Set true if this question is only visible by authenticated users."))

    sort_order = models.IntegerField(_('sort order'), default=0,
        help_text=_('The order you would like the question to be displayed.'))

    created_on = models.DateTimeField(_('created on'), default=datetime.datetime.now)
    updated_on = models.DateTimeField(_('updated on'))
    created_by = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('created by'),
        null=True, related_name="+", on_delete=models.PROTECT)
    updated_by = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('updated by'),
        null=True, related_name="+", on_delete=models.PROTECT)

    if django.VERSION >= (1, 7):
        objects = QuestionQuerySet.as_manager()
    else:
        objects = QuestionManager()

    class Meta:
        verbose_name = _("Frequent asked question")
        verbose_name_plural = _("Frequently asked questions")
        ordering = ['sort_order', 'created_on']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return ('faq_question_detail', [self.topic.slug, self.slug])

    def save(self, *args, **kwargs):
        # Set the date updated.
        self.updated_on = datetime.datetime.now()

        # Create a unique slug, if needed.
        if not self.slug:
            suffix = 0
            potential = base = slugify(self.text[:90])
            while not self.slug:
                if suffix:
                    potential = "%s-%s" % (base, suffix)
                if not Question.objects.filter(slug=potential).exists():
                    self.slug = potential
                # We hit a conflicting slug; increment the suffix and try again.
                suffix += 1

        super(Question, self).save(*args, **kwargs)

    def is_header(self):
        return self.status == Question.HEADER

    def is_active(self):
        return self.status == Question.ACTIVE
