/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
(function () {
    $.atoms.var_set_filter_selector = [
        {
            tag_code: "set_filter_selector",
            type: "combine",
            attrs: {
                name: gettext("集群选择器"),
                hookable: true,
                children: [
                    {
                        tag_code: "bk_obj_id",
                        type: "select",
                        attrs: {
                            name: gettext("过滤属性"),
                            placeholder: gettext("请选择要进行过滤的集群属性"),
                            hookable: true,
                            remote: true,
                            remote_url: function () {
                                const url = $.context.get("site_url") + "pipeline/cc_get_set_attributes/" + $.context.getBkBizId() + "/";
                                return url;
                            },
                            remote_data_init: function (resp) {
                                // 返回值格式：{
                                // "text": "xxx",
                                // "value": "xxx"
                                // }
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data;
                            },
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "bk_obj_value",
                        type: "input",
                        attrs: {
                            name: gettext("属性值范围"),
                            placeholder: gettext("请输入要过滤的属性值，多个以`,`分隔开"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    }
                ],
            }
        },
    ]
})();
