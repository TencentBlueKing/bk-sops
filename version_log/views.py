# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from version_log import config
from version_log.utils import get_version_list, get_parsed_html

logger = logging.getLogger(__name__)


def version_logs_page(request):
    """版本日志页面"""
    version_list = get_version_list()
    if version_list is None:
        logger.error('MD_FILES_DIR not found. Current path is {}'.format(config.MD_FILES_DIR))
        version_list = []  # 用无日志文件提示对用户屏蔽错误
    else:
        version_list = [{'version': version, 'date': date} for (version, date) in version_list]
    context = {
        'version_list': version_list,
        'page_title': config.PAGE_HEAD_TITLE,
        'ENTRANCE_URL': config.ENTRANCE_URL,
        'USE_HASH_URL': config.USE_HASH_URL
    }
    if config.PAGE_STYLE == 'dialog':
        return render(request, 'version_log/version_logs_dialog_page.html', context)
    else:
        return render(request, 'version_log/version_logs_page.html', context)


def version_logs_block(request):
    """版本日志数据块"""
    return render(request, 'version_log/version_logs_block.html')


def version_logs_list(request):
    """获取版本日志列表"""
    version_list = get_version_list()
    if version_list is None:
        logger.error('MD_FILES_DIR not found. Current path is {}'.format(config.MD_FILES_DIR))
        return JsonResponse({'result': False, 'code': -1, 'message': _('访问出错，请联系管理员。'), 'data': None})
    response = {'result': True, 'code': 0, 'message': _(u'日志列表获取成功'), 'data': version_list}
    return JsonResponse(response)


def get_version_log_detail(request):
    """获取单条版本日志转换结果"""
    log_version = request.GET.get('log_version')
    html_text = get_parsed_html(log_version)
    if html_text is None:
        logger.error('md file not found or log version not valid. Log version is {}'.format(log_version))
        response = {'result': False, 'code': -1, 'message': _('日志版本文件没找到，请联系管理员'), 'data': None}
        return JsonResponse(response)
    response = {'result': True, 'code': 0, 'message': _(u'日志详情获取成功'), 'data': html_text}
    return JsonResponse(response)
