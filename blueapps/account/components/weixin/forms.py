# -*- coding: utf-8 -*-
from django import forms


class WeixinAuthenticationForm(forms.Form):

    # code 格式： ...
    code = forms.CharField()
    state = forms.CharField()
