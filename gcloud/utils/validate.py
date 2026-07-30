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
import ipaddress
import logging
import socket
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse

import tldextract
import ujson as json
from django.conf import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("root")

HTTP_PLUGIN_ALLOWED_SCHEMES = {"http", "https"}
UNSAFE_IP_ATTRS = ("is_private", "is_loopback", "is_link_local", "is_multicast", "is_reserved", "is_unspecified")


def get_top_level_domain(url):
    # 提取域名部分
    extracted = tldextract.extract(url)
    # 拼合主域名和顶级域名，形成一级域名
    top_level_domain = "{}.{}".format(extracted.domain, extracted.suffix)
    return top_level_domain


def normalize_domain(domain):
    if not domain:
        return ""
    parsed = urlparse(domain if "://" in domain else "//{}".format(domain))
    try:
        hostname = parsed.hostname or domain
    except ValueError:
        hostname = domain
    return hostname.strip().strip(".").lower()


def get_url_hostname(url):
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in HTTP_PLUGIN_ALLOWED_SCHEMES:
        return None
    try:
        hostname = parsed.hostname
    except ValueError:
        return None
    if not parsed.netloc or not hostname:
        return None
    return hostname.strip().strip(".").lower()


def host_match_allowed_domains(hostname, allowed_domains):
    for allowed_domain in allowed_domains:
        allowed_domain = normalize_domain(allowed_domain)
        if not allowed_domain:
            continue

        if allowed_domain.startswith("*."):
            suffix = allowed_domain[2:]
            if hostname.endswith(".{}".format(suffix)):
                return True
            continue

        if hostname == allowed_domain or hostname.endswith(".{}".format(allowed_domain)):
            return True

    return False


def is_safe_ip_address(ip):
    if getattr(ip, "ipv4_mapped", None):
        return is_safe_ip_address(ip.ipv4_mapped)

    for attr in UNSAFE_IP_ATTRS:
        if getattr(ip, attr):
            return False
    return True


def parse_ip_address(hostname):
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        return None


def resolve_host_ips(hostname):
    try:
        address_infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except OSError:
        logger.warning("resolve http plugin domain failed: %s", hostname)
        return []

    ips = set()
    for address_info in address_infos:
        ip = address_info[4][0].split("%", 1)[0]
        try:
            ips.add(ipaddress.ip_address(ip))
        except ValueError:
            logger.warning("ignore invalid resolved ip: %s", ip)

    return list(ips)


def host_resolves_to_safe_ips(hostname):
    ip = parse_ip_address(hostname)
    if ip:
        return is_safe_ip_address(ip)

    ips = resolve_host_ips(hostname)
    if not ips:
        return False

    return all(is_safe_ip_address(ip) for ip in ips)


class RequestValidator(object, metaclass=ABCMeta):
    @abstractmethod
    def validate(self, request, *args, **kwargs):
        """
        return is_valid(bool), err(str)
        """
        raise NotImplementedError()


class ObjectJsonBodyValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
        except Exception:
            message = _("非法请求: 数据错误, 请求不是合法的Json格式 | validate")
            logger.error(message)
            return False, message

        if not isinstance(data, dict):
            return False, "request body must be a object"

        self.data = data

        return True, ""


class DomainValidator(object):
    """域名校验."""

    @staticmethod
    def validate(url):
        """
        return is_valid(bool), err(str)
        """
        if not settings.ENABLE_HTTP_PLUGIN_DOMAINS_CHECK:
            return True, []

        allowed_domains = []
        if not settings.ALLOWED_HTTP_PLUGIN_DOMAINS:
            # 默认只允许访问蓝鲸域名
            allowed_domains = [get_top_level_domain(settings.BK_URL)]
        else:
            allowed_domains = [normalize_domain(domain) for domain in settings.ALLOWED_HTTP_PLUGIN_DOMAINS.split(",")]

        hostname = get_url_hostname(url)
        if not hostname:
            return False, allowed_domains

        if not host_match_allowed_domains(hostname, allowed_domains):
            return False, allowed_domains

        if not host_resolves_to_safe_ips(hostname):
            return False, allowed_domains

        return True, []
