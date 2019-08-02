# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from mock import MagicMock, patch, call
from django.test import TestCase

from auth_backend.resources import base, django
from auth_backend.resources.base import Action
from auth_backend.resources.django import DjangoModelResource

from auth_backend.tests.mock_path import *  # noqa


class DjangoModelResourceTestCase(TestCase):

    def setUp(self):
        self.rtype = 'type_token'
        self.name = 'name_token'
        self.scope_type = 'scope_type_token'
        self.scope_name = 'scope_name_token'
        self.actions = [Action(id='view', name='view', is_instance_related=True),
                        Action(id='edit', name='edit', is_instance_related=True)]
        self.inspect = MagicMock()
        self.scope_id = 'scope_id_token'
        self.parent = MagicMock()
        self.parent.rtype = 'parent_type_token'
        self.operations = [{
            'operate_id': 'view',
            'actions_id': ['view'],
        }, {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        }]
        self.backend = MagicMock()
        self.resource_cls = MagicMock()
        self.id_field = 'id'

        self.init_kwargs = {
            'rtype': self.rtype,
            'name': self.name,
            'scope_type': self.scope_type,
            'scope_name': self.scope_name,
            'actions': self.actions,
            'inspect': self.inspect,
            'scope_id': self.scope_id,
            'parent': self.parent,
            'operations': self.operations,
            'backend': self.backend,
            'resource_cls': self.resource_cls,
            'id_field': self.id_field
        }

    def tearDown(self):
        base.resource_type_lib = {}

    @patch(DJANGO_MODEL_RESOURCE_DISPATCH_HANDLERS, MagicMock())
    def test_init(self):
        resource = DjangoModelResource(**self.init_kwargs)
        resource._dispatch_handlers.assert_called_once()

    @patch(DJANGO_MODEL_RESOURCE_DISPATCH_HANDLERS, MagicMock())
    def test_init__do_not_auto_register(self):
        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        resource._dispatch_handlers.assert_not_called()

    @patch(RESOURCE_DJANGO_POST_SAVE, MagicMock())
    @patch(RESOURCE_DJANGO_POST_DELETE, MagicMock())
    def test_dispatch_handlers(self):
        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        resource._dispatch_handlers()
        django.post_save.connect.assert_called_once_with(receiver=resource.post_save_handler,
                                                         sender=resource.resource_cls)
        django.post_delete.connect.assert_called_once_with(receiver=resource.post_delete_handler,
                                                           sender=resource.resource_cls)

    @patch(RESOURCE_REGISTER_INSTANCE, MagicMock())
    def test_post_save_handler__created(self):
        sender = 'sender_token'
        instance = 'instance_token'
        created = True

        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        resource.post_save_handler(sender=sender, instance=instance, created=created)
        resource.register_instance.assert_called_once_with(instance)

    @patch(RESOURCE_DELETE_INSTANCE, MagicMock())
    def test_post_save_handler__tomb_field_update(self):
        sender = 'sender_token'
        instance = MagicMock()
        instance.deleted = True
        created = False

        resource = DjangoModelResource(auto_register=False, tomb_field='deleted', **self.init_kwargs)
        resource.post_save_handler(sender=sender, instance=instance, created=created)
        resource.delete_instance.assert_called_once_with(instance)

    @patch(RESOURCE_UPDATE_INSTANCE, MagicMock())
    def test_post_save_handler__update(self):
        sender = 'sender_token'
        instance = 'instance_token'
        created = False

        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        resource.post_save_handler(sender=sender, instance=instance, created=created)
        resource.update_instance.assert_called_once_with(instance)

    @patch(RESOURCE_DELETE_INSTANCE, MagicMock())
    def test_post_delete_handler(self):
        sender = 'sender_token'
        instance = 'instance_token'

        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        resource.post_delete_handler(sender=sender, instance=instance)
        resource.delete_instance.assert_called_once_with(instance)

    def test_clean_instances__instances_is_none(self):
        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        resource.resource_cls = str
        self.assertIsNone(resource.clean_instances(None))

    def test_clean_str_instances(self):
        instances = 'instance'
        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        self.assertIsNotNone(resource.clean_str_instances(instances))
        resource.resource_cls.objects.get.assert_called_once_with(**{self.id_field: instances})

    def test_clean_int_instances(self):
        instances = 1
        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)
        self.assertIsNotNone(resource.clean_str_instances(instances))
        resource.resource_cls.objects.get.assert_called_once_with(**{self.id_field: instances})

    def test_clean_list_instances(self):
        resource = DjangoModelResource(auto_register=False, **self.init_kwargs)

        get_return = 'get_token'

        class AnyResource(object):
            objects = MagicMock()

        AnyResource.objects.get = MagicMock(return_value=get_return)

        resource.resource_cls = AnyResource
        instances = [AnyResource(), 2, AnyResource(), 4]
        self.assertEqual(resource.clean_list_instances(instances), [instances[0],
                                                                    'get_token',
                                                                    instances[2],
                                                                    'get_token'])
        AnyResource.objects.get.assert_has_calls([call(**{resource.id_field: 2}),
                                                  call(**{resource.id_field: 4})])
