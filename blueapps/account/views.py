# -*- coding: utf-8 -*-

import time

from django.shortcuts import render
from django.http import JsonResponse

from blueapps.account.decorators import login_exempt


@login_exempt
def login_success(request):
    """
    弹框登录成功返回页面
    """
    return render(request, 'account/login_success.html')


@login_exempt
def login_page(request):
    """
    跳转至固定页面，然后弹框登录
    """
    refer_url = request.GET.get('refer_url')

    context = {
        'refer_url': refer_url
    }
    return render(request, 'account/login_page.html', context)


def send_code_view(request):
    ret = request.user.send_code()
    return JsonResponse(ret)


def get_user_info(request):

    return JsonResponse({
                "code": 0,
                "data": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "timestamp": time.time()
                },
                "message": 'ok'
            })
