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


class MockCMDBReturnEmpty(object):
    @staticmethod
    def get_business_host_topo(*args, **kwargs):
        return []


class MockCMDB(object):
    @staticmethod
    def get_business_host_topo(*args, **kwargs):
        host_info = [
            {
                "host": {
                    "bk_host_innerip": "1.1.1.1",
                    "bk_host_outerip": "1.1.1.1",
                    "bk_host_name": "1.1.1.1",
                    "bk_host_id": 1,
                    "bk_cloud_id": 0,
                },
                "module": [{"bk_module_id": 3, "bk_module_name": "空闲机"}],
            },
            {
                "host": {
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_outerip": "2.2.2.2",
                    "bk_host_name": "2.2.2.2",
                    "bk_host_id": 2,
                    "bk_cloud_id": 0,
                },
                "module": [{"bk_module_id": 5, "bk_module_name": "test1"}],
            },
            {
                "host": {
                    "bk_host_innerip": "3.3.3.3",
                    "bk_host_outerip": "3.3.3.3",
                    "bk_host_name": "3.3.3.3",
                    "bk_host_id": 3,
                    "bk_cloud_id": 0,
                },
                "module": [{"bk_module_id": 8, "bk_module_name": "test1"}],
            },
        ]

        def match_single_rule(filter_type, data, rule):
            # Handle nested conditions structure (for IPv6 support)
            if "condition" in rule and "rules" in rule:
                condition = rule["condition"]
                sub_rules = rule["rules"]
                if condition == "OR":
                    return any(match_single_rule(filter_type, data, sub_rule) for sub_rule in sub_rules)
                elif condition == "AND":
                    return all(match_single_rule(filter_type, data, sub_rule) for sub_rule in sub_rules)
                else:
                    return False

            # Handle simple rule structure
            if "field" not in rule:
                return True  # Skip rules without field

            match_data = None
            if filter_type == "host":
                match_data = data[filter_type]
            elif filter_type == "module":
                match_data = data[filter_type][0]
            if match_data:
                host_value = match_data[rule["field"]]
                return host_value in rule["value"] if rule["operator"] == "in" else host_value not in rule["value"]

            if filter_type == "set":
                set_id_to_ip = {3: ["2.2.2.2"], 4: ["3.3.3.3"]}
                if rule["field"] == "bk_set_id":
                    ips = []
                    [ips.extend(ip) for set_id, ip in set_id_to_ip.items() if set_id in rule["value"]]
                    host_ip = data["host"]["bk_host_innerip"]
                    return host_ip in ips if rule["operator"] == "in" else host_ip not in ips

            # 其他过滤类型没有用到
            raise NotImplementedError

        if "property_filters" in kwargs:
            property_filter = kwargs["property_filters"]
            property_filter_type = ("module", "host", "set")
            result = []
            for host in host_info:
                flag = True
                for filter_type in property_filter_type:
                    key = f"{filter_type}_property_filter"
                    if key not in property_filter:
                        continue
                    rules = property_filter[key]["rules"]
                    # rules 之间目前都是 AND 关系
                    if any([not match_single_rule(filter_type, host, rule) for rule in rules]):
                        flag = False
                        break
                if flag:
                    result.append(host)
            return result
        return host_info

    @staticmethod
    def get_dynamic_group_host_list(*args, **kwargs):
        dynamic_group_data = {
            "group1": [
                {
                    "bk_host_innerip": "1.1.1.1",
                    "bk_host_outerip": "1.1.1.1",
                    "bk_host_name": "1.1.1.1",
                    "bk_host_id": 1,
                    "bk_cloud_id": 0,
                    "host_modules_id": [3],
                },
                {
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_outerip": "2.2.2.2",
                    "bk_host_name": "2.2.2.2",
                    "bk_host_id": 2,
                    "bk_cloud_id": 0,
                    "host_modules_id": [5],
                },
            ],
            "group2": [
                {
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_outerip": "2.2.2.2",
                    "bk_host_name": "2.2.2.2",
                    "bk_host_id": 2,
                    "bk_cloud_id": 0,
                    "host_modules_id": [5],
                },
                {
                    "bk_host_innerip": "3.3.3.3",
                    "bk_host_outerip": "3.3.3.3",
                    "bk_host_name": "3.3.3.3",
                    "bk_host_id": 3,
                    "bk_cloud_id": 0,
                    "host_modules_id": [8],
                },
            ],
        }
        return True, {"code": 0, "message": "success", "data": dynamic_group_data[args[-1]]}


def mock_cc_get_ips_info_by_str(tenant_id, username, bk_biz_id, ip_str):
    return {
        "result": True,
        "ip_count": 2,
        "ip_result": [
            {
                "ModuleID": 8,
                "HostID": 3,
                "InnerIP": "3.3.3.3",
                "SetID": 4,
                "Sets": [{"bk_set_id": 4}],
                "Modules": [{"bk_module_id": 8}],
                "Source": 0,
            },
            {
                "ModuleID": 5,
                "HostID": 2,
                "InnerIP": "2.2.2.2",
                "SetID": 3,
                "Sets": [{"bk_set_id": 3}],
                "Modules": [{"bk_module_id": 5}],
                "Source": 0,
            },
        ],
        "invalid_ip": [],
    }


def mock_get_client_by_user(username, stage):
    class MockCC(object):
        def __init__(self, success):
            self.success = success

        def search_biz_inst_topo(self, kwargs, path_params=None, headers=None):
            return {
                "result": self.success,
                "data": [
                    {
                        "default": 0,
                        "bk_obj_name": "业务",
                        "bk_obj_id": "biz",
                        "child": [
                            {
                                "bk_bj_name": "middle_layer",
                                "bk_obj_id": "layer",
                                "bk_inst_id": 1,
                                "bk_inst_name": "中间层",
                                "child": [
                                    {
                                        "default": 0,
                                        "bk_obj_name": "集群",
                                        "bk_obj_id": "set",
                                        "child": [
                                            {
                                                "default": 0,
                                                "bk_obj_name": "模块",
                                                "bk_obj_id": "module",
                                                "bk_inst_id": 5,
                                                "bk_inst_name": "test1",
                                            },
                                            {
                                                "default": 0,
                                                "bk_obj_name": "模块",
                                                "bk_obj_id": "module",
                                                "bk_inst_id": 6,
                                                "bk_inst_name": "test2",
                                            },
                                            {
                                                "default": 0,
                                                "bk_obj_name": "模块",
                                                "bk_obj_id": "module",
                                                "bk_inst_id": 7,
                                                "bk_inst_name": "test3",
                                            },
                                        ],
                                        "bk_inst_id": 3,
                                        "bk_inst_name": "set2",
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": "集群",
                                        "bk_obj_id": "set",
                                        "child": [
                                            {
                                                "default": 0,
                                                "bk_obj_name": "模块",
                                                "bk_obj_id": "module",
                                                "bk_inst_id": 8,
                                                "bk_inst_name": "test1",
                                            },
                                            {
                                                "default": 0,
                                                "bk_obj_name": "模块",
                                                "bk_obj_id": "module",
                                                "bk_inst_id": 9,
                                                "bk_inst_name": "test2",
                                            },
                                        ],
                                        "bk_inst_id": 4,
                                        "bk_inst_name": "set3",
                                    },
                                ],
                            },
                        ],
                        "bk_inst_id": 2,
                        "bk_inst_name": "蓝鲸",
                    }
                ],
                "message": "error",
            }

        def search_dynamic_group(self, page, path_params=None, headers=None, limit=None):
            return {
                "result": True,
                "data": {
                    "count": 1,
                    "info": [
                        {"id": "group1", "bk_obj_id": "host", "name": "group1-name"},
                        {"id": "group2", "bk_obj_id": "host", "name": "group2-name"},
                    ],
                },
            }

        def get_biz_internal_module(self, kwargs, path_params=None, headers=None):
            return {
                "result": self.success,
                "data": {
                    "bk_set_id": 2,
                    "bk_set_name": "空闲机池",
                    "module": [
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_module_id": 3,
                            "bk_obj_name": "模块",
                            "bk_module_name": "空闲机",
                        },
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_module_id": 4,
                            "bk_obj_name": "模块",
                            "bk_module_name": "故障机",
                        },
                    ],
                },
                "message": "error",
            }

    class MockClient(object):
        def __init__(self, success):
            self.api = MockCC(success)

    return MockClient(mock_get_client_by_user.success)
