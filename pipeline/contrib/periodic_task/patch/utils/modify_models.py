# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

Examples
========
my_app/models.py
----------------

    from django.db import models

    class CustomerType(models.Model):
        name = models.CharField(max_length=50)

        def __unicode__(self):
            return self.name

    class Customer(models.Model):
        name = models.CharField(max_length=50)
        type = models.ForeignKey('CustomerType')
        is_active = models.BooleanField(default=True, blank=True)
        employer = models.CharField(max_length=100)

        def __unicode__(self):
            return self.name

another_app/models.py
---------------------

    from django.db import models
    from django.contrib.auth.models import User

    from djangoplus.modify_models import ModifiedModel

    class City(models.Model):
        name = models.CharField(max_length=50)

        def __unicode__(self):
            return self.name

    class HelperCustomerType(ModifiedModel):
        class Meta:
            model = 'my_app.CustomerType'

        description = models.TextField()

    class HelperCustomer(ModifiedModel):
        class Meta:
            model = 'my_app.Customer'
            exclude = ('employer',)

        type = models.CharField(max_length=50)
        address = models.CharField(max_length=100)
        city = models.ForeignKey(City)

        def __unicode__(self):
            return '%s - %s'%(self.pk, self.name)

    class HelperUser(ModifiedModel):
        class Meta:
            model = User

        website = models.URLField(blank=True, verify_exists=False)

"""

import types

from django.core.exceptions import ImproperlyConfigured
from django.db import models

try:
    from django.db.models import get_model
except Exception:
    from django.apps import apps

    get_model = apps.get_model


class ModifiedModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(ModifiedModelMetaclass, cls).__new__(cls, name, bases, attrs)

        if name == "ModifiedModel" and bases[0] == object:
            return new_class

        try:
            meta = attrs["Meta"]()
        except KeyError:
            raise ImproperlyConfigured("Helper class %s hasn't a Meta subclass!" % name)

        # Find model class for this helper
        if isinstance(getattr(meta, "model", None), str):
            model_class = get_model(*meta.model.split("."))
        elif issubclass(getattr(meta, "model", None), models.Model):
            model_class = meta.model
        else:
            raise ImproperlyConfigured("Model informed by Meta subclass of %s is improperly!" % name)

        def remove_field(f_name):
            # Removes the field form local fields list
            model_class._meta.local_fields = [f for f in model_class._meta.local_fields if f.name != f_name]

            # Removes the field setter if exists
            if hasattr(model_class, f_name):
                delattr(model_class, f_name)

        # Removes fields setted in attribute 'exclude'
        if isinstance(getattr(meta, "exclude", None), (list, tuple)):
            for f_name in meta.exclude:
                remove_field(f_name)

        # Calls 'contribute_to_class' from field to sender class
        for f_name, field in list(attrs.items()):
            if isinstance(field, models.Field):
                # Removes the field if it already exists
                remove_field(f_name)

                # Appends the new field to model class
                field.contribute_to_class(model_class, f_name)

        # Attaches methods
        for m_name, func in list(attrs.items()):
            if callable(func) and isinstance(func, types.FunctionType) or isinstance(func, (classmethod, property)):
                setattr(model_class, m_name, func)

        new_class._meta = meta

        return new_class


class ModifiedModel(object, metaclass=ModifiedModelMetaclass):
    """
    Make your inheritance from this class and set a Meta subclass with attribute
    'model' with the model class you want to modify: add/replace/exclude fields
    and/or add/replace methods.
    """
