#log/forms.py
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from dash.models import Author

# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Password Confirmation", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    username.help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."

    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

class ProfileForm(forms.ModelForm):

    firstName = forms.CharField(label="First Name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    lastName = forms.CharField(label="Last Name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    displayName = forms.CharField(label="Display Name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'class': 'form-control'}))
    github = forms.CharField(label="Github", widget=forms.TextInput(attrs={'class': 'form-control'}))
    bio = forms.CharField(label="Bio", widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Author

        fields = ('firstName', 'lastName', 'displayName', 'email', 'github', 'bio')
