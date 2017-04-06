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

    content = forms.CharField(
        label='',
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control content_box', 'name': 'content', 'rows': '15',
                   'cols': '50'}
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
        ('FOAF', 'Friends of a Friend'),
        ('FRIENDS', 'Friends'),
        ('PRIVATE', 'Private'),
        ('SERVERONLY', 'Server only')
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
                   'placeholder': 'Visible to', 'disabled': False}
        )
    )


    unlisted = forms.BooleanField(
        label='Unlisted',
        widget=forms.CheckboxInput(
            attrs={'class': 'form-inline private', 'id':'id_unlisted', 'name': 'unlisted'}
        ),
        required = False
    )

    attachImage = forms.ImageField(
        label='Attach an image',
        required=False,
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'name': 'image',
                   'accept': 'image/*'}
        )
    )

    post_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={'name': 'post_id', 'id':'id_post_id'}
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
    """
    contentType = forms.CharField(
        widget=forms.HiddenInput(),
        initial='text/plain',
        max_length=32
    )
    """
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
#class FriendRequestForm(ModelForm):
    #class Meta:
        #model  = Follow
        #fields = ['followee','follower']
        #widgets = {'followee': forms.HiddenInput()}
