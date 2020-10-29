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
    $.atoms.cc_update_world_status = [
        {
            tag_code: "set_select_method",
            type: "radio",
            attrs: {
                name: gettext("传参形式"),
                hookable: false,
                items: [
                    {value: "name", name: gettext("Set名称")},
                    {value: "id", name: gettext("Set ID")},
                ],
                default: "name",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "set_select_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "set_list",
            type: "textarea",
            attrs: {
                name: gettext("大区范围"),
                placeholder: gettext("多个集群使用英文','分割"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "set_select_method",
                    type: "change",
                    action: function () {
                        this.value = '';
                    }
                },
            ]
        },
        {
            tag_code: "set_status",
            type: "select",
            attrs: {
                name: gettext("服务状态"),
                allowCreate: true,
                placeholder: gettext('请选择'),
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_search_status_options/' + $.context.getBkBizId() + '/',
                remote_data_init: function (resp) {
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
        },
    ]

})();
