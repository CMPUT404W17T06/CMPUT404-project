from django import forms
from django.forms import ModelForm

class PostForm(forms.Form):
    title = forms.CharField(
        label='',
        max_length=32,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'title',
                   'placeholder': 'title'}
        )
    )
    description = forms.CharField(
        label='',
        max_length=140,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'description',
                   'placeholder': 'description'}
        )
    )

    content = forms.CharField(
        label='',
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control content_box', 'name': 'content', 'rows': '15',
                   'cols': '50'}
        )
    )

    contentTypeChoices = (
        ('text/markdown', 'Markdown'),
        ('text/plain', 'Plaintext'),
    )
    contentType = forms.ChoiceField(
        label='',
        choices=contentTypeChoices,
        widget=forms.Select(
            attrs={'class': 'form-control', 'name': 'contentType'}
        ),
        initial='Markdown'
    )

    attachImage = forms.ImageField(
        label='',
        required=False,
        widget=forms.FileInput(
            attrs={'class':'filestyle', 'data-buttonBefore':"true",'data-buttonText':"Attach Image",
            'data-iconName':"glyphicon glyphicon-picture", 'name': 'image','accept': 'image/*'}
        )
    )

    categories = forms.CharField(
        label='',
        max_length=128,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'categories',
                   'placeholder': 'categories'}
        )
    )

    visibilityChoices = (
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
        ('FRIENDS', 'Friends'),
        ('FOAF', 'Friends of a Friend'),
        ('SERVERONLY', 'Server only'),
        ('UNLISTED', 'Unlisted')
    )
    visibility = forms.ChoiceField(
        label='',
        choices=visibilityChoices,
        widget=forms.Select(
            attrs={'class': 'form-control', 'name': 'visibility',
            'id':'id_visibility', 'placeholder': 'visibility'}
        ),
        initial='PUBLIC'
    )

    visibleTo = forms.CharField(
        label='',
        max_length=128,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control private', 'name': 'visibleTo', 'id':'id_visibleTo',
                   'placeholder': 'visible to', 'disabled': False}
        )
    )


class CommentForm(forms.Form):
    comment = forms.CharField(
        label='',
        required=True,
        widget=forms.Textarea(
            attrs={ 'name': 'content', 'class':'form-control comment_box', 'placeholder': 'Add a comment...', 'rows':'2'}
        )
    )
    post_id = forms.CharField(
        widget=forms.HiddenInput(),
        initial='',
        max_length=32
    )

    contentTypeChoices = (
        ('text/markdown', 'Markdown'),
        ('text/plain', 'Plaintext'),
    )
    contentType = forms.ChoiceField(
        label='',
        choices=contentTypeChoices,
        widget=forms.Select(
            attrs={'class': 'form-control type_selector contentType', 'name': 'contentType'}
        ),
        initial='Markdown'
    )
