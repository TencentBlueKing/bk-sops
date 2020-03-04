# -*- coding: utf-8 -*-
from django import forms


class AuthenticationForm(forms.Form):
    # bk_token format: KH7P4-VSFi_nOEoV3kj0ytcs0uZnGOegIBLV-eM3rw8
    bk_token = forms.CharField()
