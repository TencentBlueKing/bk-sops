# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from datetime import datetime

import pytz
from django import forms
from django.utils import timezone


class GetTaskListForm(forms.Form):
    is_started = forms.BooleanField(required=False)
    is_finished = forms.BooleanField(required=False)
    keyword = forms.CharField(required=False)
    executor = forms.CharField(required=False)
    create_method = forms.CharField(required=False)
    template_id = forms.CharField(required=False)
    without_count = forms.BooleanField(required=False)
    template_ids = forms.CharField(required=False)
    is_child_taskflow = forms.BooleanField(required=False)
    create_time_start = forms.CharField(
        required=False,
        help_text=(
            "创建时间起始，格式：YYYY-MM-DD HH:MM:SS、YYYY-MM-DD HH:MM:SS +HHMM"
            "、YYYY-MM-DD HH:MM:SS+HHMM、YYYY-MM-DDTHH:MM:SSZ 或 YYYY-MM-DD"
        ),
    )
    create_time_end = forms.CharField(
        required=False,
        help_text=(
            "创建时间结束，格式：YYYY-MM-DD HH:MM:SS、YYYY-MM-DD HH:MM:SS +HHMM"
            "、YYYY-MM-DD HH:MM:SS+HHMM、YYYY-MM-DDTHH:MM:SSZ 或 YYYY-MM-DD"
        ),
    )

    def clean_template_ids(self):
        template_ids = self.cleaned_data["template_ids"]
        if not template_ids:
            return []
        return [id.strip() for id in template_ids.split(",") if id.strip()]

    def _parse_datetime(self, date_str, is_end_date=False):
        """
        解析日期字符串，支持多种格式（包括带时区的格式）
        参考：gcloud/utils/dates.py 中的 format_datetime 方法使用 %z 格式输出时区
        """
        if not date_str:
            return None
        date_str = date_str.strip()

        # 处理 ISO 8601 格式（带 Z 或时区偏移）
        # 先尝试处理 ISO 8601 格式，因为格式更明确
        if "T" in date_str or date_str.endswith("Z"):
            iso_formats = [
                "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 UTC格式：2024-01-01T12:00:00Z
                "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 UTC格式（带微秒）：2024-01-01T12:00:00.000Z
                "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 带时区：2024-01-01T12:00:00+0800
                "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 带时区和微秒：2024-01-01T12:00:00.000+0800
            ]
            for fmt in iso_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # ISO 8601 Z 格式需要转换为 UTC
                    if fmt.endswith("Z"):
                        dt = dt.replace(tzinfo=pytz.UTC)
                    # 如果已经是带时区的，直接返回
                    if timezone.is_aware(dt):
                        return dt
                except ValueError:
                    continue

        # 尝试解析带时区的格式（%z 格式，支持 +HHMM 或 -HHMM）
        # 注意：Python strptime 的 %z 只支持 +HHMM 或 -HHMM 格式，不支持 +HH:MM
        timezone_formats = [
            "%Y-%m-%d %H:%M:%S %z",  # 2024-01-01 12:00:00 +0800 (带空格)
            "%Y-%m-%d %H:%M:%S%z",  # 2024-01-01 12:00:00+0800 (不带空格)
            "%Y-%m-%d %H:%M %z",  # 2024-01-01 12:00 +0800
            "%Y-%m-%d %H:%M%z",  # 2024-01-01 12:00+0800
        ]

        for fmt in timezone_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # Python 3.7+ 中 strptime 会自动处理 %z，返回带时区的 datetime
                if timezone.is_aware(dt):
                    return dt
            except ValueError:
                continue

        # 尝试解析不带时区的格式
        naive_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ]

        for fmt in naive_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # 如果是日期格式，设置为当天的开始或结束时间
                if fmt == "%Y-%m-%d":
                    # 开始日期设置为00:00:00，结束日期设置为23:59:59
                    if is_end_date:
                        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    else:
                        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                # 转换为带时区的datetime（使用系统默认时区）
                return timezone.make_aware(dt)
            except ValueError:
                continue

        raise forms.ValidationError(
            f"无法解析日期格式: {date_str}，支持的格式："
            "YYYY-MM-DD HH:MM:SS、YYYY-MM-DD HH:MM:SS +HHMM、"
            "YYYY-MM-DD HH:MM:SS+HHMM、YYYY-MM-DDTHH:MM:SSZ 或 YYYY-MM-DD"
        )

    def clean_create_time_start(self):
        return self._parse_datetime(self.cleaned_data.get("create_time_start"), is_end_date=False)

    def clean_create_time_end(self):
        return self._parse_datetime(self.cleaned_data.get("create_time_end"), is_end_date=True)
