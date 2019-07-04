# -*- coding: UTF-8 -*-

from django import forms
from .models import Host


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = '__all__'