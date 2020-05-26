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

from copy import deepcopy

from django.test import TestCase

from pipeline_web.constants import PWE
from pipeline_web.parser.clean import PipelineWebTreeCleaner
from pipeline_web.tests.parser.data import (
    id_list,
    id_list3,
    WEB_PIPELINE_DATA,
    WEB_PIPELINE_WITH_SUB_PROCESS
)


class TestPipelineWebTreeCleaner(TestCase):

    def setUp(self):
        web_pipeline_tree = deepcopy(WEB_PIPELINE_DATA)
        web_pipeline_tree[PWE.activities][id_list[3]][PWE.labels] = [
            {
                'label': 'label11',
                'group': 'group1'
            },
            {
                'label': 'label12',
                'group': 'group1'
            }
        ]
        web_pipeline_tree[PWE.activities][id_list[4]][PWE.labels] = [
            {
                'label': 'label21',
                'group': 'group2'
            }
        ]
        cleaner = PipelineWebTreeCleaner(web_pipeline_tree)
        self.cleaner_simple = cleaner

        web_pipeline_tree_with_sub = deepcopy(WEB_PIPELINE_WITH_SUB_PROCESS)
        web_pipeline_tree_with_sub[PWE.activities][id_list[3]][PWE.labels] = [
            {
                'label': 'label11',
                'group': 'group1'
            },
            {
                'label': 'label12',
                'group': 'group1'
            }
        ]
        sub_pipeline = web_pipeline_tree_with_sub[PWE.activities][id_list[4]][PWE.pipeline]
        sub_pipeline[PWE.activities][id_list3[3]][PWE.labels] = [
            {
                'label': 'label21',
                'group': 'group2'
            }
        ]
        cleaner_with_sub = PipelineWebTreeCleaner(web_pipeline_tree_with_sub)
        self.cleaner_with_sub = cleaner_with_sub

    def test_clean__without_subprocess(self):
        nodes_attr = self.cleaner_simple.clean()
        assert_attr = {
            id_list[3]: {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            id_list[4]: {
                PWE.labels: [
                    {
                        'label': 'label21',
                        'group': 'group2'
                    }
                ]
            }
        }
        self.assertEqual(nodes_attr, assert_attr)
        self.assertEqual(self.cleaner_simple.pipeline_tree, WEB_PIPELINE_DATA)

    def test_clean__with_subprocess(self):
        nodes_attr = self.cleaner_with_sub.clean(with_subprocess=True)
        assert_attr = {
            id_list[3]: {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            PWE.subprocess_detail: {
                id_list[4]: {
                    id_list3[3]: {
                        PWE.labels: [
                            {
                                'label': 'label21',
                                'group': 'group2'
                            }
                        ]
                    }
                }
            }
        }
        self.assertEqual(nodes_attr, assert_attr)
        self.assertEqual(self.cleaner_with_sub.pipeline_tree, WEB_PIPELINE_WITH_SUB_PROCESS)

    def test_replace_id(self):
        nodes_attr = {
            id_list[3]: {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            PWE.subprocess_detail: {
                id_list[4]: {
                    id_list3[3]: {
                        PWE.labels: [
                            {
                                'label': 'label21',
                                'group': 'group2'
                            }
                        ]
                    }
                }
            }
        }
        nodes_id_maps = {
            PWE.activities: {
                id_list[3]: 'new_id3',
                id_list[4]: 'new_id4'
            },
            PWE.subprocess_detail: {
                'new_id4': {
                    PWE.activities: {
                        id_list3[3]: 'new_id5'
                    }
                }
            }
        }
        new_nodes_attr = PipelineWebTreeCleaner.replace_id(nodes_attr, nodes_id_maps, with_subprocess=True)
        self.assertEqual(new_nodes_attr, {
            'new_id3': {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            PWE.subprocess_detail: {
                'new_id4': {
                    'new_id5': {
                        PWE.labels: [
                            {
                                'label': 'label21',
                                'group': 'group2'
                            }
                        ]
                    }
                }
            }
        })

    def test_to_web__without_subprocess(self):
        nodes_attr = {
            id_list[3]: {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            id_list[4]: {
                PWE.labels: [
                    {
                        'label': 'label21',
                        'group': 'group2'
                    }
                ]
            }
        }
        self.cleaner_simple.clean()
        self.cleaner_simple.to_web(nodes_attr)
        self.assertEqual(self.cleaner_simple.pipeline_tree, self.cleaner_simple.origin_data)

    def test_to_web__with_subprocess__recursive_nodes_attr(self):
        nodes_attr = {
            id_list[3]: {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            PWE.subprocess_detail: {
                id_list[4]: {
                    id_list3[3]: {
                        PWE.labels: [
                            {
                                'label': 'label21',
                                'group': 'group2'
                            }
                        ]
                    }
                }
            }
        }
        self.cleaner_with_sub.clean(with_subprocess=True)
        self.cleaner_with_sub.to_web(nodes_attr, with_subprocess=True)
        self.assertEqual(self.cleaner_with_sub.pipeline_tree, self.cleaner_with_sub.origin_data)

    def test_to_web__with_subprocess__plain_nodes_attr(self):
        nodes_attr = {
            id_list[3]: {
                PWE.labels: [
                    {
                        'label': 'label11',
                        'group': 'group1'
                    },
                    {
                        'label': 'label12',
                        'group': 'group1'
                    }
                ]
            },
            id_list3[3]: {
                PWE.labels: [
                    {
                        'label': 'label21',
                        'group': 'group2'
                    }
                ]
            }
        }
        self.cleaner_with_sub.clean(with_subprocess=True)
        self.cleaner_with_sub.to_web(nodes_attr, with_subprocess=True)
        self.assertEqual(self.cleaner_with_sub.pipeline_tree, self.cleaner_with_sub.origin_data)
