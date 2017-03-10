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
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'categories',
                   'placeholder': 'categories', 'disabled': True}
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
