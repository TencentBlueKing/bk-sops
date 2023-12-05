# -*- coding: utf-8 -*-
import logging

from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.job.base import get_sops_var_dict_from_log_text

logger = logging.getLogger(__name__)


MULTI_LINE_TEXT1 = """
<SOPS_VAR>key1:value1</SOPS_VAR>
gsectl -rwxr-xr-x 1 root
<SOPS_VAR>key2:value2</SOPS_VAR>
gsectl -rwxr-xr-x 1 root
"""

MULTI_LINE_TEXT2 = """
<SOPS_VAR>key1:
value1</SOPS_VAR>
abcd
<SOPS_VAR>key
2:value2</SOPS_VAR>
"""

MULTI_LINE_TEXT3 = """<SOPS_VAR>
key1: value1
key2: value2
</SOPS_VAR>
"""


MULTI_LINE_TEXT4 = """
<SOPS_VAR>
key1: value1 key2:value2
</SOPS_VAR>
"""


MULTI_LINE_TEXT5 = "<SOPS_VAR> key1: value1\r\nkey2:value2 </SOPS_VAR>"


class GetSOPSVarDictFromLogText(TestCase):
    def test_single_line_log(self):
        text = "<SOPS_VAR>key1:value1</SOPS_VAR> gsectl -rwxr-xr-x 1 root<SOPS_VAR>key2:value2</SOPS_VAR>"
        result = get_sops_var_dict_from_log_text(text, logger)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

        text2 = "<SOPS_VAR> key1 : value1 </SOPS_VAR> gsectl -rwxr-xr-x 1 root<SOPS_VAR>key2:value2</SOPS_VAR>"
        result2 = get_sops_var_dict_from_log_text(text2, logger)
        self.assertEqual(result2, {" key1 ": " value1 ", "key2": "value2"})

    def test_multiple_line_log(self):
        test_cases = [
            (MULTI_LINE_TEXT1, {"key1": "value1", "key2": "value2"}),
            (MULTI_LINE_TEXT2, {"key1": "\nvalue1", "key\n2": "value2"}),
            (MULTI_LINE_TEXT3, {"\nkey1": " value1\nkey2: value2\n"}),
            (MULTI_LINE_TEXT4, {"\nkey1": " value1 key2:value2\n"}),
            (MULTI_LINE_TEXT5, {" key1": " value1\r\nkey2:value2 "}),
        ]
        for log, expected_result in test_cases:
            result = get_sops_var_dict_from_log_text(log, logger)
            self.assertEqual(result, expected_result)
