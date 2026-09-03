# -*- coding: utf-8 -*-
from django.test import TestCase

from gcloud.analysis_statistics.mako_expression_inventory import (
    analyze_expression,
    classify_location,
    collect_template_expressions,
)


class AnalyzeExpressionTestCase(TestCase):
    def test_plain_variable_is_not_policy_hit(self):
        result = analyze_expression("${ip_list}")
        self.assertFalse(result["hits_policy"])
        self.assertFalse(result["uses_injected_module"])
        self.assertFalse(result["has_deep_attr"])
        self.assertEqual(result["risk_level"], "潜在unknown_root")
        self.assertEqual(result["unknown_roots"], ["ip_list"])

    def test_injected_module_and_deep_attr(self):
        result = analyze_expression("${os.path.join(a, b)}")
        self.assertTrue(result["uses_injected_module"])
        self.assertEqual(result["used_modules"], ["os"])
        self.assertTrue(result["has_deep_attr"])
        self.assertGreaterEqual(result["attr_depth"], 2)
        self.assertFalse(result["hits_policy"])
        self.assertEqual(result["risk_level"], "潜在unknown_root")

    def test_format_is_unconditional_hit_and_not_v2_matchable(self):
        result = analyze_expression('${"gamedb.{}.xzj.db".format(name)}')
        self.assertTrue(result["hits_unconditional"])
        self.assertTrue(result["hits_policy"])
        self.assertEqual(result["risk_level"], "无条件阻断")
        self.assertFalse(result["v2_matchable"])
        self.assertTrue(any(item.startswith("forbidden_method:format") for item in result["reasons"]))

    def test_custom_filter_is_unconditional_hit(self):
        result = analyze_expression("${cc|str_set_name}")
        self.assertTrue(result["hits_unconditional"])
        self.assertTrue(any(item.startswith("unsupported_filter:") for item in result["reasons"]))

    def test_builtin_filter_is_allowed(self):
        result = analyze_expression("${name | trim}")
        self.assertFalse(result["hits_unconditional"])
        self.assertFalse(any(item.startswith("unsupported_filter:") for item in result["reasons"]))

    def test_bare_caller_is_not_policy_hit(self):
        result = analyze_expression("${caller}")
        self.assertFalse(result["hits_whitelist"])
        self.assertFalse(result["hits_unconditional"])
        self.assertNotEqual(result["risk_level"], "仅enforce阻断")

    def test_reserved_namespace_attribute_is_whitelist_hit(self):
        result = analyze_expression("${caller.body()}")
        self.assertTrue(result["hits_whitelist"])
        self.assertTrue(any(item.startswith("reserved_namespace:") for item in result["reasons"]))

    def test_user_module_attr_is_not_whitelist_hit(self):
        result = analyze_expression("${res_data._module}")
        self.assertFalse(result["hits_whitelist"])
        self.assertFalse(any(item == "private_attr:_module" for item in result["reasons"]))

    def test_import_deep_attr_is_whitelist_hit(self):
        result = analyze_expression("${json.codecs.builtins.exec('1')}")
        self.assertTrue(result["hits_whitelist"])
        self.assertTrue(
            any(
                item.startswith("import_attr_depth:") or item.startswith("dangerous_attr:")
                for item in result["reasons"]
            )
        )

    def test_dangerous_attr_is_whitelist_hit(self):
        result = analyze_expression("${os.path.os.popen('id')}")
        self.assertTrue(result["hits_whitelist"])
        self.assertTrue(any(item.startswith("dangerous_attr:") for item in result["reasons"]))

    def test_system_and_loop_are_extra_whitelist(self):
        result = analyze_expression("${_system.executor}")
        self.assertFalse(result["hits_policy"])
        self.assertEqual(result["root_names"], ["_system"])
        self.assertNotIn("unknown_root:_system", result["reasons"])

    def test_listcomp_local_name_is_not_unknown_root(self):
        result = analyze_expression("${[x * 2 for x in items]}")
        self.assertEqual(result["root_names"], ["items"])
        self.assertNotIn("x", result["root_names"])


class CollectTemplateExpressionsTestCase(TestCase):
    def test_collects_node_gateway_and_constant_locations(self):
        tree = {
            "activities": {
                "n1": {
                    "id": "n1",
                    "name": "HTTP",
                    "type": "ServiceActivity",
                    "component": {
                        "code": "bk_http_request",
                        "data": {"body": {"value": '${os.path.join(work_dir, "a")}'}},
                    },
                }
            },
            "gateways": {
                "g1": {
                    "type": "ExclusiveGateway",
                    "conditions": {"e1": {"evaluate": "${re.compile(pat).pattern}"}},
                }
            },
            "constants": {"${caller}": {"value": "${caller}"}},
            "outputs": ["${ip_list}"],
        }

        rows = collect_template_expressions(tree)
        by_expr = {item["expr"]: item for item in rows}

        self.assertIn('${os.path.join(work_dir, "a")}', by_expr)
        self.assertEqual(by_expr['${os.path.join(work_dir, "a")}']["location_type"], "节点输入")
        self.assertEqual(by_expr['${os.path.join(work_dir, "a")}']["plugin_code"], "bk_http_request")
        self.assertEqual(by_expr['${os.path.join(work_dir, "a")}']["node_name"], "HTTP")
        self.assertTrue(by_expr['${os.path.join(work_dir, "a")}']["uses_injected_module"])
        self.assertTrue(by_expr['${os.path.join(work_dir, "a")}']["has_deep_attr"])

        self.assertEqual(by_expr["${re.compile(pat).pattern}"]["location_type"], "网关条件")
        self.assertTrue(by_expr["${re.compile(pat).pattern}"]["has_deep_attr"])

        self.assertEqual(by_expr["${caller}"]["location_type"], "全局变量")
        self.assertFalse(by_expr["${caller}"]["hits_policy"])

        self.assertEqual(classify_location("$.outputs[0]"), "输出")
