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
    $.atoms.cc_replace_fault_machine = [
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
            tag_code: "cc_host_replace_detail",
            type: "datatable",
            attrs: {
                name: gettext("主机详情"),
                empty_text: gettext("请至少添加一条数据"),
                editable: true,
                add_btn: true,
                columns: [
                    {
                        tag_code: "cc_fault_ip",
                        type: "input",
                        attrs: {
                            name: gettext("故障机IP"),
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "cc_new_ip",
                        type: "input",
                        attrs: {
                            name: gettext("替换机IP"),
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    }
                ],
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();