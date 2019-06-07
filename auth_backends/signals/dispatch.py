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

from django.db.models.signals import post_save

from . import model_bulk_create
from .handlers import model_post_create_handler, model_bulk_create_handler


def dispatch_model_post_create():
    post_save.connect(
        model_post_create_handler,
        dispatch_uid='_model_post_create_handler',
    )


def dispatch_model_bulk_create():
    model_bulk_create.connect(
        model_bulk_create_handler,
        dispatch_uid='_model_bulk_create_handler'
    )


def dispatch():
    dispatch_model_post_create()
    dispatch_model_bulk_create()
