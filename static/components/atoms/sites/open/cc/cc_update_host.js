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
(function () {
    $.atoms.cc_update_host = [
        {
            tag_code: "cc_biz_host_property",
            type: "combine",
            attrs: {
                "name": gettext("主机属性"),
                hookable: true,
                children: [
                    {
                        tag_code: "biz_cc_id",
                        type: "select",
                        attrs: {
                            name: gettext("业务"),
                            hookable: false,
                            remote: true,
                            remote_url: $.context.site_url + 'pipeline/cc_get_business_list/',
                            remote_data_init: function (resp) {
                                return resp.data;
                            },
                            disabled: $.context.project.from_cmdb,
                            value: $.context.project.from_cmdb ? $.context.project.bk_biz_id : '',
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "cc_host_property",
                        type: "select",
                        attrs: {
                            name: gettext("主机属性"),
                            placeholder: gettext("请选择需要更新的主机属性"),
                            hookable: true,
                            remote: true,
                            remote_url: function () {
                                url = $.context.project.from_cmdb ? $.context.site_url + 'pipeline/cc_search_object_attribute/host/' + $.context.project.bk_biz_id + '/' : '';
                                return url
                            },
                            remote_data_init: function (resp) {
                                return resp.data;
                            },
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "biz_cc_id",
                                type: "init",
                                action: function () {
                                    cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id').value;
                                    this.items = [];
                                    if (cc_id !== '') {
                                        this.remote_url = $.context.site_url + 'pipeline/cc_search_object_attribute/host/' + cc_id + '/';
                                        this.remoteMethod();
                                    }
                                }
                            },
                            {
                                source: "biz_cc_id",
                                type: "change",
                                action: function (value) {
                                    this._set_value('');
                                    this.items = [];
                                    if (value !== '') {
                                        this.remote_url = $.context.site_url + 'pipeline/cc_search_object_attribute/host/' + value + '/';
                                        this.remoteMethod();
                                    }
                                }
                            }
                        ],
                    },
                ]
            }
        },
        {
            tag_code: "cc_host_ip",
            type: "textarea",
            attrs: {
                name: gettext("主机内网IP"),
                placeholder: gettext("请输入主机内网IP，多个用换行符分隔"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "cc_host_prop_value",
            type: "input",
            attrs: {
                name: gettext("属性值"),
                placeholder: gettext("请输入更新后的属性值"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
    ]
})();