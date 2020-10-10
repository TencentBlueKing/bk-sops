# -*- coding: utf-8 -*-

import logging

from django.conf.urls import url

from gcloud.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def monitor_get_strategy(request, biz_cc_id):
    client = get_client_by_user(request.user.username)
    response = client.monitor.query_strategy({"bk_biz_id": biz_cc_id})
    if not response["result"]:
        message = _(u"查询监控(Monitor)的策略[app_id=%s]接口monitor.query_strategy返回失败: %s") % (biz_cc_id, response["message"])
        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)
    strategy_list = []
    for strategy in response["data"]:
        strategy_list.append({"value": strategy["id"], "text": strategy["name"]})
    return JsonResponse({"result": True, "data": strategy_list})


monitor_urlpatterns = [url(r"^monitor_get_strategy/(?P<biz_cc_id>\d+)/$", monitor_get_strategy)]
