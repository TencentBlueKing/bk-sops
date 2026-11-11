# -*- coding: utf-8 -*-
"""监控屏蔽插件 2.1 结束处理方式与旧版本请求兼容性回归（多租户版）。"""
import importlib
import logging
from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pipeline.core.data.base import DataObject

from pipeline_plugins.components.collections.sites.open.monitor.end_policy import ShieldEndPolicyMixin

PREFIX = "pipeline_plugins.components.collections.sites.open.monitor"
MISSING = object()

SCOPE_INPUTS = {
    "bk_alarm_shield_info": {"bk_alarm_shield_scope": "business"},
    "bk_alarm_shield_target": ["all"],
    "bk_alarm_shield_reason": "maintenance",
    "bk_alarm_shield_begin_time": "2026-10-27 10:00:00",
    "bk_alarm_shield_end_time": "2026-10-27 11:00:00",
    "bk_alarm_time_type": "0",
    "bk_alarm_shield_duration": "60",
}
STRATEGY_INPUTS = {
    "bk_alarm_shield_strategy": [123, 456],
    "bk_alarm_shield_IP": "",
    "bk_alarm_shield_reason": "maintenance",
    "bk_dimension_list": [],
    "bk_dimension_select_type": "and",
    "bk_alarm_shield_begin_time": "2026-10-27 10:00:00",
    "bk_alarm_shield_end_time": "2026-10-27 11:00:00",
    "bk_alarm_time_type": "0",
    "bk_alarm_shield_duration": "60",
}
PARENT_DATA = {"biz_cc_id": 2, "executor": "operator", "tenant_id": "system"}

CASES = [
    ("alarm_shield", "v2_1", "MonitorAlarmShieldService", SCOPE_INPUTS),
    ("alarm_shield_strategy", "v2_1", "MonitorAlarmShieldStrategyService", STRATEGY_INPUTS),
]


def make_client(result=True):
    client = MagicMock()
    client.api.add_shield.return_value = {
        "result": result,
        "data": {"id": 789},
        "message": "success" if result else "denied",
    }
    return client


def input_key(item):
    return item["key"] if isinstance(item, dict) else item.key


class ShieldEndPolicyServiceTest(TestCase):
    def run_plugin(self, kind, version, service_name, inputs, end_policy=MISSING, result=True):
        module = importlib.import_module("{}.{}.{}".format(PREFIX, kind, version))
        service = getattr(module, service_name)()
        service.logger = logging.getLogger("test.monitor")
        payload = deepcopy(inputs)
        if end_policy is not MISSING:
            payload["bk_alarm_shield_end_policy"] = end_policy
        data = DataObject(payload)
        parent = DataObject(PARENT_DATA)
        client = make_client(result)
        # plugin_execute / get_client_by_username 定义在 v2_0 模块，v2_1 仅继承
        base_module = "{}.{}.v2_0".format(PREFIX, kind)
        with patch("{}.get_client_by_username".format(base_module), return_value=client):
            success = service.plugin_execute(data, parent)
        return success, data, client.api.add_shield.call_args_list

    def test_new_versions_forward_default_and_explicit_policy(self):
        for kind, version, service_name, inputs in CASES:
            for given in [MISSING, None, "", "notify_once", "close"]:
                with self.subTest(kind=kind, given=given):
                    success, data, calls = self.run_plugin(kind, version, service_name, inputs, given)
                    self.assertTrue(success)
                    self.assertEqual(len(calls), 1)
                    (body,) = calls[0].args
                    self.assertEqual(body["end_policy"], "close" if given == "close" else "notify_once")
                    self.assertEqual(calls[0].kwargs["headers"], {"X-Bk-Tenant-Id": "system"})
                    self.assertEqual(data.get_one_of_outputs("shield_id"), 789)

    def test_invalid_policy_stops_before_request(self):
        for kind, version, service_name, inputs in CASES:
            with self.subTest(kind=kind):
                success, data, calls = self.run_plugin(kind, version, service_name, inputs, "invalid")
                self.assertFalse(success)
                self.assertEqual(calls, [])
                self.assertIn("notify_once", str(data.get_one_of_outputs("ex_data")))

    def test_old_versions_ignore_new_input_and_keep_original_body(self):
        cases = [
            ("alarm_shield", "MonitorAlarmShieldService", SCOPE_INPUTS),
            ("alarm_shield_strategy", "MonitorAlarmShieldStrategyService", STRATEGY_INPUTS),
        ]
        for kind, service_name, inputs in cases:
            with self.subTest(kind=kind):
                _, _, old_calls = self.run_plugin(kind, "v2_0", service_name, inputs)
                _, _, with_new_input = self.run_plugin(kind, "v2_0", service_name, inputs, "close")
                self.assertEqual(old_calls, with_new_input)
                (body,) = old_calls[0].args
                self.assertNotIn("end_policy", body)

    def test_new_versions_only_add_policy_to_previous_body(self):
        cases = [
            ("alarm_shield", "MonitorAlarmShieldService", SCOPE_INPUTS),
            ("alarm_shield_strategy", "MonitorAlarmShieldStrategyService", STRATEGY_INPUTS),
        ]
        for kind, service_name, inputs in cases:
            with self.subTest(kind=kind):
                _, _, old_calls = self.run_plugin(kind, "v2_0", service_name, inputs)
                _, _, new_calls = self.run_plugin(kind, "v2_1", service_name, inputs, "close")
                new_body = dict(new_calls[0].args[0])
                self.assertEqual(new_body.pop("end_policy"), "close")
                self.assertEqual(new_body, old_calls[0].args[0])

    def test_monitor_rejection_is_not_reported_as_success(self):
        for kind, version, service_name, inputs in CASES:
            with self.subTest(kind=kind):
                success, data, calls = self.run_plugin(kind, version, service_name, inputs, "close", result=False)
                self.assertFalse(success)
                (body,) = calls[0].args
                self.assertEqual(body["end_policy"], "close")
                self.assertEqual(data.get_one_of_outputs("shield_id"), "")

    def test_component_metadata_and_service_mixin(self):
        cases = [
            ("alarm_shield", "MonitorAlarmShieldComponent"),
            ("alarm_shield_strategy", "MonitorAlarmShieldStrategyComponent"),
        ]
        for kind, component_name in cases:
            old = importlib.import_module("{}.{}.v2_0".format(PREFIX, kind))
            new = importlib.import_module("{}.{}.v2_1".format(PREFIX, kind))
            old_cls, new_cls = getattr(old, component_name), getattr(new, component_name)
            with self.subTest(code=new_cls.code):
                self.assertEqual(old_cls.code, new_cls.code)
                self.assertEqual(old_cls.version, "2.0")
                self.assertEqual(new_cls.version, "2.1")
                self.assertTrue(new_cls.form.endswith("/v2_1.js"))
                old_keys = [input_key(item) for item in old_cls.bound_service().inputs_format()]
                new_keys = [input_key(item) for item in new_cls.bound_service().inputs_format()]
                self.assertNotIn("bk_alarm_shield_end_policy", old_keys)
                self.assertIn("bk_alarm_shield_end_policy", new_keys)
                self.assertFalse(issubclass(old_cls.bound_service, ShieldEndPolicyMixin))
                self.assertTrue(issubclass(new_cls.bound_service, ShieldEndPolicyMixin))
