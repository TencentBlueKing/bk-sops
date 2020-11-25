# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from mock import patch, MagicMock, call

from django.test import TestCase

from pipeline_web.wrapper import PipelineTemplateWebWrapper


class UnfoldSubprocessTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch("pipeline_web.wrapper.replace_template_id", MagicMock())
    def test_unfold_1_layer_subprocess(self):
        layer_1_t1_tree = {
            "activities": {},
            "constants": {"${param}": {"value": ""}, "${c1}": {"value": "constant_value"}},
        }

        # prepare pipeline data
        pipeline_data = {
            "activities": {
                "subproc_1": {
                    "type": "SubProcess",
                    "template_id": "layer_1_t1",
                    "version": "v1",
                    "constants": {"${param}": {"value": "${parent_param}"}},
                }
            },
            "constants": {"${parent_param}": "${another_constants}"},
        }

        # prepare template model mock
        template_model = MagicMock()
        get_return = MagicMock()
        get_return.get_pipeline_tree_by_version = MagicMock(return_value=layer_1_t1_tree)
        template_model.objects.get = MagicMock(return_value=get_return)

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_data, template_model)

        template_model.objects.get.assert_called_once_with(pipeline_template__template_id="layer_1_t1")
        get_return.get_pipeline_tree_by_version.assert_called_once_with("v1")

        self.assertDictEqual(
            pipeline_data,
            {
                "activities": {
                    "subproc_1": {
                        "type": "SubProcess",
                        "template_id": "layer_1_t1",
                        "version": "v1",
                        "pipeline": {
                            "id": "subproc_1",
                            "activities": {},
                            "constants": {
                                "${param}": {"value": "${parent_param}"},
                                "${c1}": {"value": "constant_value"},
                            },
                        },
                    }
                },
                "constants": {"${parent_param}": "${another_constants}"},
            },
        )

    @patch("pipeline_web.wrapper.replace_template_id", MagicMock())
    def test_unfold_2_layer_subprocess(self):
        layer_2_t1_tree = {
            "activities": {
                "subproc_2": {
                    "type": "SubProcess",
                    "template_id": "layer_2_t2",
                    "version": "v2",
                    "constants": {"${param}": {"value": "${parent_param2}"}},
                }
            },
            "constants": {"${parent_param2}": {"value": ""}, "${c1}": {"value": "constant_value_1"}},
        }

        layer_2_t2_tree = {
            "activities": {},
            "constants": {"${param}": {"value": ""}, "${c2}": {"value": "constant_value_2"}},
        }

        # prepare pipeline data
        pipeline_data = {
            "activities": {
                "subproc_1": {
                    "type": "SubProcess",
                    "template_id": "layer_2_t1",
                    "version": "v1",
                    "constants": {"${parent_param2}": {"value": "${parent_param1}"}},
                }
            },
            "constants": {"${parent_param1}": "${another_constants}"},
        }

        def get_pipeline_tree_by_version(v):
            return {"v1": layer_2_t1_tree, "v2": layer_2_t2_tree}[v]

        # prepare template model mock
        template_model = MagicMock()
        get_return = MagicMock()
        get_return.get_pipeline_tree_by_version = MagicMock(side_effect=get_pipeline_tree_by_version)
        template_model.objects.get = MagicMock(return_value=get_return)

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_data, template_model)

        template_model.objects.get.assert_has_calls(
            [call(pipeline_template__template_id="layer_2_t1"), call(pipeline_template__template_id="layer_2_t2")]
        )
        get_return.get_pipeline_tree_by_version.assert_has_calls([call("v1"), call("v2")])

        self.assertDictEqual(
            pipeline_data,
            {
                "activities": {
                    "subproc_1": {
                        "type": "SubProcess",
                        "template_id": "layer_2_t1",
                        "version": "v1",
                        "pipeline": {
                            "id": "subproc_1",
                            "activities": {
                                "subproc_2": {
                                    "type": "SubProcess",
                                    "template_id": "layer_2_t2",
                                    "version": "v2",
                                    "pipeline": {
                                        "id": "subproc_2",
                                        "activities": {},
                                        "constants": {
                                            "${param}": {"value": "${parent_param2}"},
                                            "${c2}": {"value": "constant_value_2"},
                                        },
                                    },
                                }
                            },
                            "constants": {
                                "${parent_param2}": {"value": "${parent_param1}"},
                                "${c1}": {"value": "constant_value_1"},
                            },
                        },
                    }
                },
                "constants": {"${parent_param1}": "${another_constants}"},
            },
        )

    @patch("pipeline_web.wrapper.replace_template_id", MagicMock())
    def test_unfold_3_layer_subprocess(self):
        layer_3_t1_tree = {
            "activities": {
                "subproc_2": {
                    "type": "SubProcess",
                    "template_id": "layer_3_t2",
                    "version": "v2",
                    "constants": {"${parent_param3}": {"value": "${parent_param2}"}},
                }
            },
            "constants": {"${parent_param2}": {"value": ""}, "${c1}": {"value": "constant_value_1"}},
        }

        layer_3_t2_tree = {
            "activities": {
                "subproc_3": {
                    "type": "SubProcess",
                    "template_id": "layer_3_t3",
                    "version": "v3",
                    "constants": {"${param}": {"value": "${parent_param3}"}},
                }
            },
            "constants": {"${parent_param3}": {"value": ""}, "${c2}": {"value": "constant_value_2"}},
        }

        layer_3_t3_tree = {
            "activities": {},
            "constants": {"${param}": {"value": ""}, "${c3}": {"value": "constant_value_3"}},
        }

        # prepare pipeline data
        pipeline_data = {
            "activities": {
                "subproc_1": {
                    "type": "SubProcess",
                    "template_id": "layer_3_t1",
                    "version": "v1",
                    "constants": {"${parent_param2}": {"value": "${parent_param1}"}},
                }
            },
            "constants": {"${parent_param1}": "${another_constants}"},
        }

        def get_pipeline_tree_by_version(v):
            return {"v1": layer_3_t1_tree, "v2": layer_3_t2_tree, "v3": layer_3_t3_tree}[v]

        # prepare template model mock
        template_model = MagicMock()
        get_return = MagicMock()
        get_return.get_pipeline_tree_by_version = MagicMock(side_effect=get_pipeline_tree_by_version)
        template_model.objects.get = MagicMock(return_value=get_return)

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_data, template_model)

        template_model.objects.get.assert_has_calls(
            [
                call(pipeline_template__template_id="layer_3_t1"),
                call(pipeline_template__template_id="layer_3_t2"),
                call(pipeline_template__template_id="layer_3_t3"),
            ]
        )
        get_return.get_pipeline_tree_by_version.assert_has_calls([call("v1"), call("v2"), call("v3")])

        self.assertDictEqual(
            pipeline_data,
            {
                "activities": {
                    "subproc_1": {
                        "type": "SubProcess",
                        "template_id": "layer_3_t1",
                        "version": "v1",
                        "pipeline": {
                            "id": "subproc_1",
                            "activities": {
                                "subproc_2": {
                                    "type": "SubProcess",
                                    "template_id": "layer_3_t2",
                                    "version": "v2",
                                    "pipeline": {
                                        "id": "subproc_2",
                                        "activities": {
                                            "subproc_3": {
                                                "type": "SubProcess",
                                                "template_id": "layer_3_t3",
                                                "version": "v3",
                                                "pipeline": {
                                                    "id": "subproc_3",
                                                    "activities": {},
                                                    "constants": {
                                                        "${param}": {"value": "${parent_param3}"},
                                                        "${c3}": {"value": "constant_value_3"},
                                                    },
                                                },
                                            }
                                        },
                                        "constants": {
                                            "${parent_param3}": {"value": "${parent_param2}"},
                                            "${c2}": {"value": "constant_value_2"},
                                        },
                                    },
                                }
                            },
                            "constants": {
                                "${parent_param2}": {"value": "${parent_param1}"},
                                "${c1}": {"value": "constant_value_1"},
                            },
                        },
                    }
                },
                "constants": {"${parent_param1}": "${another_constants}"},
            },
        )
