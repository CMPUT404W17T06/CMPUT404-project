from django import forms


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
            attrs={'class': 'form-control', 'name': 'content',
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
            attrs={'class': 'form-control', 'name': 'visibility', 'placeholder': 'visibility'}
        ),
        initial='PUBLIC'
    )

    unlisted = forms.BooleanField(
        label='Unlisted',
        widget=forms.CheckboxInput(
            attrs={'class': 'form-control', 'name': 'unlisted'}
        ),
        required = False
    )

    visibleTo = forms.CharField(
        label='',
        max_length=128,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'visibleTo',
                   'placeholder': 'Visible to', 'disabled': True}
        )
    )

    attachImage = forms.ImageField(
        label='Attach an image',
        required=False,
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'name': 'image',
                   'accept': 'image/*'}
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
