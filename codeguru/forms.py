from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CgGroup, CENTER_CHOICES


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        # user.picture = self.cleaned_data['picture']

        if commit:
            user.save()
        return user


class NewGroupForm(forms.ModelForm):

    class Meta:
        model = CgGroup
        fields = ('name', 'center')
