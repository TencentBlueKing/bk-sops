# -*- coding: utf-8 -*-
import base64
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from pipeline_plugins.components.utils import cc_get_ips_info_by_str

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
logger = logging.getLogger("root")

SCRIPT_CONTENT = """
file_path=$1

if [ ! -f "${file_path}" ]; then
  exit 1
fi

base64 ${file_path}
"""
SCRIPT_TYPE = "1"
JOB_WAIT_TIME_OUT = 60


def get_job_content(remote_files, operator, biz_cc_id):
    """
    根据ip、文件路径获取远程服务器的以base64编码的文件内容
    @param remote_files: 文件集合 [{"file_path":"", "ip":"只支持单个ip", "job_account":""}]
    @param operator: 操作人员
    @param biz_cc_id: 业务id
    @return: {
                "success": [
                    {"file_name": "file_name", "content": "content", "ip": "1.1.1.2"}
                ],
                "failure": [
                    {"file_name": "file_name", "ip": "1.1.1.1", "message": "error"}
                ]
            }
    """
    client = get_client_by_user(operator)
    job_execute_suc_records = []
    job_execute_fail_records = []

    ip_str = ",".join([remote_file["ip"] for remote_file in remote_files])
    ip_info = cc_get_ips_info_by_str(
        username=operator,
        biz_cc_id=biz_cc_id,
        ip_str=ip_str,
        use_cache=False,
    )
    ip_list_result = [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in ip_info["ip_result"]]
    _ip_list_result = [_ip["InnerIP"] for _ip in ip_info["ip_result"]]

    for remote_file in remote_files:
        script_param = remote_file["file_path"]
        _, file_name = os.path.split(script_param)
        job_account = remote_file["job_account"]

        if remote_file["ip"] not in _ip_list_result:
            job_execute_fail_records.append(
                {
                    "file_name": file_name,
                    "ip": remote_file["ip"],
                    "message": "ip 信息在 cmdb 不存在",
                    "ip_list": remote_file["ip"],
                }
            )
            continue
        for ip_list in ip_list_result:
            if remote_file["ip"] != ip_list["ip"]:
                continue
            job_kwargs = {
                "bk_biz_id": biz_cc_id,
                "account": job_account,
                "ip_list": [ip_list],
                "script_param": base64.b64encode(script_param.encode("utf-8")).decode("utf-8"),
                "script_type": SCRIPT_TYPE,
                "script_content": base64.b64encode(SCRIPT_CONTENT.encode("utf-8")).decode("utf-8"),
            }
            job_result = client.job.fast_execute_script(job_kwargs)
            logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))
            if job_result["result"]:
                job_instance_id = job_result["data"]["job_instance_id"]
                job_execute_suc_records.append(({"file_name": file_name, "ip": remote_file["ip"]}, job_instance_id))
            else:
                job_execute_fail_records.append(
                    {
                        "file_name": file_name,
                        "ip": remote_file["ip"],
                        "message": job_result["message"],
                        "ip_list": ip_list,
                    }
                )

    polling_job_results = []
    with ThreadPoolExecutor(max_workers=10) as t:
        all_task = [t.submit(get_job_instance_log, task, operator, biz_cc_id) for task in job_execute_suc_records]
        wait(all_task, return_when=ALL_COMPLETED)
        for job_result in all_task:
            polling_job_results.append(job_result.result())
    # 获取轮询结果
    result_success = []
    for polling_job_result in polling_job_results:
        if polling_job_result["result"]:
            result_success.append(
                {
                    "file_name": polling_job_result["key"]["file_name"],
                    "content": polling_job_result["log_content"],
                    "ip": polling_job_result["key"]["ip"],
                }
            )
        else:
            job_execute_fail_records.append(
                {
                    "file_name": polling_job_result["key"]["file_name"],
                    "ip": polling_job_result["key"]["ip"],
                    "message": polling_job_result["message"],
                }
            )
    result = {"failure": job_execute_fail_records, "success": result_success}

    return result


def get_job_instance_log(job_instance_record, operator, bk_biz_id):
    """
    轮询job执行结果
    @param job_instance_record: [({"file_name": file_name, "ip": remote_file["ip"]}, job_instant_id)]
    @param operator: admin
    @param bk_biz_id: 123
    @return:
    """
    client = get_client_by_user(operator)
    get_job_instance_log_kwargs = {"job_instance_id": job_instance_record[1], "bk_biz_id": bk_biz_id}
    get_job_instance_log_return = client.job.get_job_instance_log(get_job_instance_log_kwargs)
    if not get_job_instance_log_return["result"]:
        return {"result": False, "message": get_job_instance_log_return["message"], "key": job_instance_record[0]}
    else:
        start_time = time.time()
        while time.time() < start_time + JOB_WAIT_TIME_OUT:
            job_status = get_job_instance_log_return["data"][0]["status"]
            if job_status == 3:
                return {
                    "result": True,
                    "key": job_instance_record[0],
                    "log_content": "\n".join(
                        [
                            job_log["step_results"][0]["ip_logs"][0]["log_content"]
                            for job_log in get_job_instance_log_return["data"]
                        ]
                    ),
                }
            elif job_status > 3:
                return {
                    "result": False,
                    "message": get_job_instance_log_return["message"],
                    "key": job_instance_record[0],
                }
            # 休眠1s再去查询接口
            time.sleep(1)
            get_job_instance_log_return = client.job.get_job_instance_log(get_job_instance_log_kwargs)
        return {"result": False, "message": _("请求job执行结果超时"), "key": job_instance_record[0]}
