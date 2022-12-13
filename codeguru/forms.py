from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CgGroup, Center, Profile
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))
    first_name = forms.CharField(required=True, label=_("First Name"))
    last_name = forms.CharField(required=True, label=_("Last Name"))
    phone = forms.CharField(required=True, max_length=10, min_length=10, label=_("Phone Number"))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "phone", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if User.objects.filter(email=user.email).exists():
            raise ValidationError("Email already exists")

        if commit:
            user.save()

            p = Profile(user=user, phone=self.cleaned_data['phone'])
            p.save()
            
        return user

class NewCenterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewCenterForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Center
        fields = ('name', 'ticker')

class NewGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewGroupForm, self).__init__(*args, **kwargs)
        # self.fields['center'].widget.attrs['style'] = "width:50px"

    class Meta:
        model = CgGroup
        fields = ('name', 'center')
