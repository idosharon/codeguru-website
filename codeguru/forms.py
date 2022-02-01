from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CgGroup, CENTER_CHOICES
from django.utils.translation import gettext_lazy as _

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
        return user


class NewGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewGroupForm, self).__init__(*args, **kwargs)
        self.fields['center'].widget.attrs['style'] = "width:50px"

    class Meta:
        model = CgGroup
        fields = ('name', 'center')
