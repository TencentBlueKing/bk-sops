# -*- coding: utf-8 -*-

import logging

from django.conf.urls import url

from api import BKMonitorClient
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse

from gcloud.iam_auth.utils import check_and_raise_raw_auth_fail_exception

logger = logging.getLogger("root")


def monitor_get_strategy(request, biz_cc_id):
    client = BKMonitorClient(username=request.user.username)
    response = client.search_alarm_strategy(bk_biz_id=biz_cc_id)
    if not response["result"]:
        message = _(
            f"请求策略失败: 请求[监控平台]的策略[ID: {biz_cc_id}]返回失败: {response['message']}.请重试, 如持续失败可联系管理员处理 | monitor_get_strategy"
        )
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(response, message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)
    strategy_list = []
    for strategy in response["data"]:
        strategy_list.append({"value": strategy["id"], "text": strategy["name"]})
    return JsonResponse({"result": True, "data": strategy_list})


monitor_urlpatterns = [url(r"^monitor_get_strategy/(?P<biz_cc_id>\d+)/$", monitor_get_strategy)]
