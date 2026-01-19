# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.variables.collections import common


class CommonVariablesSupplementTestCase(TestCase):
    def test_StaffGroupSelector(self):
        pipeline_data = {"executor": "user", "biz_cc_id": "1", "tenant_id": "tenant"}
        value = ["1", "operator"]  # 1 is custom, operator is cc

        var = common.StaffGroupSelector(value=value, context={}, pipeline_data=pipeline_data, name="test")

        # Case 1: Missing pipeline data
        var.pipeline_data = {}
        with self.assertRaisesRegex(Exception, "executor and biz_cc_id"):
            var.get_value()

        # Case 2: get_notify_receivers fail
        var.pipeline_data = pipeline_data

        with mock.patch("pipeline_plugins.variables.collections.common.StaffGroupSet") as MockStaffGroupSet:
            MockStaffGroupSet.objects.filter.return_value.values_list.return_value = ["u1,u2"]

            with mock.patch("pipeline_plugins.variables.collections.common.get_notify_receivers") as mock_get:
                mock_get.return_value = {"result": False, "message": "error"}

                with self.assertRaises(common.ApiRequestError):
                    var.get_value()

                # Case 3: Success
                mock_get.return_value = {"result": True, "data": "u1,u2,u3"}
                self.assertEqual(var.get_value(), "u1,u2,u3")

    def test_TextValueSelect(self):
        # Test process_info_value dict branch
        info_value = {"value": 1, "text": "t", "text_not_selected": "tn", "value_not_selected": "vn"}
        res = common.TextValueSelect.process_info_value(info_value)
        self.assertEqual(res, [1])

        # Test process_info_value dict branch (not match keys)
        info_value = {"value": 1, "other": 2}
        res = common.TextValueSelect.process_info_value(info_value)
        self.assertEqual(res, info_value)

    def test_FormatSupportDateTime(self):
        # Test default format
        value = {"datetime": "2023-01-01 12:00:00"}
        var = common.FormatSupportDateTime(value=value, context={}, pipeline_data={}, name="test")
        self.assertEqual(var.get_value(), "2023-01-01 12:00:00")

        # Test custom format
        value = {"datetime": "2023-01-01 12:00:00", "datetime_format": "%Y/%m/%d"}
        var = common.FormatSupportDateTime(value=value, context={}, pipeline_data={}, name="test")
        self.assertEqual(var.get_value(), "2023/01/01")

    def test_Select(self):
        # Test single select
        var = common.Select(value="val", context={}, pipeline_data={}, name="test")
        self.assertEqual(var.get_value(), "val")

        # Test multi select
        var = common.Select(value=["v1", "v2"], context={}, pipeline_data={}, name="test")
        self.assertEqual(var.get_value(), "v1,v2")
