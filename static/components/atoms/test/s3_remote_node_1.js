/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
(function(){
    $.atoms.s3_pause1_node = [
        {
            tag_code: "test_radio",
            type: "radio",
            attrs: {
                name: gettext("测试RADIO"),
                items: [
                    {value: "1", name: "选项1"},
                    {value: "2", name: "选项2"},
                    {value: "3", name: "选项3"},
                ],
                default: "2",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "test_testarea",
            type: "textarea",
            attrs: {
                name: gettext("测试文本框"),
                placeholder: gettext("提示"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ],
                default: "2",
            }
        },
        {
            tag_code: "test_input",
            type: "input",
            attrs: {
                name: gettext("通天塔"),
                placeholder: gettext("可为空"),
                hookable: true
            },
        },
    ]
})();