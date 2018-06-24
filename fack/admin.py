from __future__ import absolute_import

from django import forms
from django.contrib import admin
from .models import Question, Topic


class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class QuestionAdminForm(forms.ModelForm):
    excerpt = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 80,
            'style': 'font-family:monospace'
        }),
        help_text=
        '<a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">reStructuredText Quick Reference</a>'
    )
    answer = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 20,
            'cols': 80,
            'style': 'font-family:monospace'
        }),
        help_text=
        '<a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">reStructuredText Quick Reference</a>'
    )

    class Meta:
        model = Question
        fields = [
            'topic',
            'text',
            'slug',
            'excerpt',
            'answer',
            'status',
            'protected',
        ]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'sort_order', 'created_by', 'created_on',
                    'updated_by', 'updated_on', 'status']
    list_editable = ['sort_order', 'status']

    form = QuestionAdminForm
    prepopulated_fields = {'slug': ('text',)}

    def save_model(self, request, obj, form, change):
        '''
        Update created-by / modified-by fields.
        
        The date fields are upadated at the model layer, but that's not got
        access to the user.
        '''
        # If the object's new update the created_by field.
        if not change:
            obj.created_by = request.user

        # Either way update the updated_by field.
        obj.updated_by = request.user

        # Let the superclass do the final saving.
        return super(QuestionAdmin, self).save_model(request, obj, form, change)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Topic, TopicAdmin)
