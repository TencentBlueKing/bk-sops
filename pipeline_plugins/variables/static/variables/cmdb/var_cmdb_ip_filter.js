/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
(function () {
    $.atoms.var_cmdb_ip_filter = [
        {
            tag_code: "ip_filter",
            type: "combine",
            attrs: {
                name: gettext("IP过滤器"),
                hookable: true,
                children: [
                    {
                        tag_code: "origin_ips",
                        type: "textarea",
                        attrs: {
                            name: gettext("原始IP"),
                            placeholder: gettext("IP为【IP】（云区域ID为0）、【云区域ID:IP】格式之一，多个用换行分隔"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "gse_agent_status",
                        type: "select",
                        attrs: {
                            name: gettext("GSE AGENT状态"),
                            items: [
                                {text: "在线", value: 1},
                                {text: "不在线", value: 0},
                                {text: "不过滤", value: 2}
                            ],
                            default: 0,
                            hookable: true,
                            validation: []
                        }
                    }
                ],
            }
        },
    ]
})();
