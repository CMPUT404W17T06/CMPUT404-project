from django import forms


class PostForm(forms.Form):
    title = forms.CharField(
        label='title',
        max_length=32,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'title',
                   'placeholder': 'title'}
        )
    )
    description = forms.CharField(
        label='description',
        max_length=140,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'content',
                   'placeholder': 'description'}
        )
    )
    contentType = forms.CharField(
        widget=forms.HiddenInput(),
        initial='text/plain',
        max_length=32
    )
    content = forms.CharField(
        label='content',
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'name': 'content', 'rows': '15',
                   'cols': '50'}
        )
    )
    categories = forms.CharField(
        label='categories',
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
        label='visibility',
        choices=visibilityChoices,
        widget=forms.Select(
            attrs={'class': 'form-control', 'name': 'visibility'}
        ),
        initial='PUBLIC'
    )

    visibleTo = forms.CharField(
        label='categories',
        max_length=128,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'visibleTo',
                   'placeholder': 'Visible to', 'disabled': True}
        )
    )


class CommentForm(forms.Form):
    comment = forms.CharField(
        label='comment',
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'name': 'content', 'rows': '2',
                   'cols': '50'}
        )
    )
    contentType = forms.CharField(
        widget=forms.HiddenInput(),
        initial='text/plain',
        max_length=32
    )
    """
    contentType = (
        ('text/plain', 'Plaintext'),
        ('text/markdown', 'Markdown'),
    )
    contentType = forms.ChoiceField(
        label='contentType',
        choices=visibilityChoices,
        widget=forms.Select(
            attrs={'class': 'form-control', 'name': 'visibility'}
        ),
        initial='PUBLIC'
    )
    """
