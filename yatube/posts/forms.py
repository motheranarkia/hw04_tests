from django import forms

from .models import Post

from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            'text': _('Writer'),
        }
        help_texts = {
            'text': _('Текст нового поста'),
        }
        widgets = {
            "text": forms.Textarea(attrs={
                'class': 'form-control',
                'cols': '40',
                'rows': '10'
            }),
            'group': forms.Select(attrs={
                'class': 'form-control',
            })
        }
