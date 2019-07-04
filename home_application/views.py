# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from blueking.component.client import ComponentClient
from blueapps.account.models import User
from blueking.component.shortcuts import get_client_by_user
import base64
import re
from django.core import serializers
from blueapps.account.decorators import login_exempt
import time
from  .forms import HostForm
from .models import Host, DiskUsage
from blueking.component.shortcuts import get_client_by_request


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    # 耗时任务，发送邮件（用delay执行方法）
    return render(request, 'home_application/home.html')

def helloworld(request):
    if request.method == 'GET':
        return render(request, 'home_application/helloworld.html')
    elif request.method == 'POST':
        text_content = request.POST['text_input']
        if text_content == "Hello Blueking":
            output = "Congratulation！"
            return render(request, 'home_application/helloworld.html', locals())
        else:
            return render(request, 'home_application/helloworld.html')

def index(request):
    return render(request, 'home_application/index.html')

def forms(request):
    if request.method == 'GET':
        return render(request, 'home_application/forms.html')
    elif request.method == 'POST':
        host_form = HostForm(request.POST)
        res = dict(result=False)
        if host_form.is_valid():
            host_form.save()
            res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')

def tables(request):
    list = Host.objects.all()
    return render(request, 'home_application/tables.html', locals())


def get_capacity():
    user = User.objects.get(username='550407948')
    client = get_client_by_user(user.username)  # 这里是周期任务，不能通过request请求client
    fast_execute_script_result = fast_execute_script(client)
    # 如果快速脚本调用成功，执行log日志查询，获取执行内容
    if fast_execute_script_result['message'] == 'success':
        job_instance_id = fast_execute_script_result['data']['job_instance_id']
        get_job_instance_log_result = get_job_instance_log(client, job_instance_id)

        # 如果日志查询成功，提取内容
        if get_job_instance_log_result['message'] == 'success':
            # 匹配log_content规则
            result = get_job_instance_log_result['data'][0]['step_results'][0]['ip_logs'][0]
            disk = DiskUsage.objects.create(value=result['log_content'], add_time=result['end_time'], host_id=1)
            return HttpResponse(disk, content_type='application/json')

        else:
            return None


def fast_execute_script(client):
    """
        快速执行脚本函数
    """
    script_content = base64.urlsafe_b64encode(b"df -h /|sed '1d'|awk '{print $5}'|sed 's/%//g'|sed -n 1p")
    script_param = base64.urlsafe_b64encode(b'/')
    ip_list = [
        {
            "bk_cloud_id": 0,
            "ip": "10.0.1.80"
        }
    ]
    # 参数
    kwargs = {'bk_biz_id': 4, 'script_content': script_content, 'script_type': 1, 'ip_list': ip_list, 'account': 'root'}
    return client.job.fast_execute_script(kwargs)
def get_job_instance_log(client, job_instance_id):
    """
    对作业执行具体日志查询函数
    """

    kwargs = {'job_instance_id' : job_instance_id, 'bk_biz_id': 4}
    time.sleep(2)  # todo 延时2s, 快速执行脚本需要一定的时间， 后期可以用celery串行两个函数
    return client.job.get_job_instance_log(kwargs)

def model_data_format(usages):
    usage_add_time = []
    usage_value = []
    for usage in usages:
        usage_add_time.append(usage.add_time.strftime("%Y/%m/%d %H:%M:%S"))
        usage_value.append(usage.value)
    return usage_add_time, usage_value

def disk_use(request):
    list = DiskUsage.objects.all()

    return render(request, 'home_application/diskuse.html', locals())

@login_exempt
def api_disk_usage(request):
    """
    磁盘使用率API接口
    """
    ip = request.GET.get('ip', '')
    system = request.GET.get('system', '')
    mounted = request.GET.get('disk', '')

    if ip and system and mounted:
        disk_usages = DiskUsage.objects.filter(host__ip=ip, host__os=system, host__partition=mounted)
        if not disk_usages:
            return JsonResponse({
                "result": False,
                "data": [],
                "message": '查询不存在'
            })



    else:
        return JsonResponse({
            "result": False,
            "data": [],
            "message": '参数不完整'
        })
    disk_usage_add_time, disk_usage_value = model_data_format(disk_usages)
    data_list ={

            "xAxis": disk_usage_add_time,
            "series": [
                {
                    "name": "磁盘使用率",
                    "type": "line",
                    "data": disk_usage_value
                }
            ]
        }
    return JsonResponse({
        "code": 0,
        "result": True,
        "data": data_list,
        "message": 'ok'
    })


def usage_data_view(request):
    return render(request, 'home_application/diskuse.html', locals())


def get_usage_data(request):
    """
    调用自主接入接口api
    """
    if request.method == 'GET':
        client = get_client_by_request(request)
        ip = request.GET.get('ip', '')
        system = request.GET.get('system', '')
        disk = request.GET.get('disk', '')
        kwargs = {'ip':ip, 'system':system, 'disk':disk}
        usage = client.disk_query.get_disk_usage(kwargs)
        return JsonResponse(usage)
