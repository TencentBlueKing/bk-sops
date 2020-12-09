# -*- coding: utf-8 -*-
import datetime
import logging
import re
import time

# 正则表达式预编译
date_regx = re.compile(r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})")

logger = logging.getLogger("component")


def get_end_time_by_duration(start_time, duration):
    dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = (dt + datetime.timedelta(minutes=duration)).strftime("%Y-%m-%d %H:%M:%S")
    return end_time


def choose_time(time_type, start_time, end_time, duration, date_regx=date_regx):
    # 手动输入
    if time_type == 0:
        start_match = re.findall(date_regx, start_time)
        end_match = re.findall(date_regx, end_time)
        if not start_match or not end_match:
            raise ValueError
        start_time = start_match[0]
        end_time = end_match[0]
    # 从当前时间开始，仅输入持续时间
    elif time_type == 1:
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        end_time = get_end_time_by_duration(start_time, int(duration))
    # 输入开始时间和持续时间
    elif time_type == 2:
        start_match = re.findall(date_regx, start_time)
        if not start_match:
            raise ValueError
        start_time = start_match[0]
        end_time = get_end_time_by_duration(start_time, int(duration))
    return start_time, end_time
