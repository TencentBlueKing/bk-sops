# -*- coding: utf-8 -*-
from django import forms

from blueapps.account.models import User


class UserCreationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username',)
