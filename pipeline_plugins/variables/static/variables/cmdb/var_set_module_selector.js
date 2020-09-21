/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
(function () {
    $.atoms.var_set_module_selector = [
        {
            tag_code: "set_module_selector",
            type: "combine",
            attrs: {
                name: "集群模块选择器",
                hookable: true,
                children: [
                    {
                        tag_code: "bk_set_id",
                        type: "select",
                        attrs: {
                            name: gettext("选择集群"),
                            hookable: true,
                            remote: true,
                            remote_url: function () {
                                const url = $.context.get("site_url") + "pipeline/cc_get_set/" + $.context.getBkBizId() + "/";
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
                        tag_code: "bk_module_id",
                        type: "select",
                        attrs: {
                            name: gettext("选择模块"),
                            hookable: true,
                            multiple: true,
                            remote: true,
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
                        },
                        methods: {
                            _tag_init: function () {
                                this.items = []
                            }
                        },
                        events: [
                            {
                                source: "bk_set_id",
                                type: "init",
                                action: function (value) {
                                    if (value !== "") {
                                        //这里传入集群ID
                                        this.remote_url = $.context.get("site_url") + "pipeline/cc_get_module/" + $.context.getBkBizId() + "/" + value + "/";
                                        this.remoteMethod();
                                    }

                                }
                            },
                            {
                                source: "bk_set_id",
                                type: "change",
                                action: function (value) {
                                    this._set_value('');
                                    if (value !== "") {
                                        //这里传入集群ID
                                        this.remote_url = $.context.get("site_url") + "pipeline/cc_get_module/" + $.context.getBkBizId() + "/" + value + "/";
                                        this.remoteMethod();
                                    }
                                }
                            }
                        ]
                    }
                ],
            }
        },
    ]
})();
