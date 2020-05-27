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
    $.atoms.alarm_shield_strategy = [
        {
            tag_code: "bk_alarm_shield_strategy",
            type: "select",
            attrs: {
                name: gettext("策略"),
                multiple: true,
                remote: true,
                remote_url: $.context.site_url + "pipeline/monitor_get_strategy/" + $.context.getBkBizId() + "/",
                remote_data_init: function (resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "bk_alarm_shield_IP",
            type: "input",
            attrs: {
                name: gettext("IP"),
                hookable: true,
                placeholder: gettext("请输入主机IP，多个用逗号分隔"),
            }
        },
        {
            tag_code: "bk_alarm_shield_strategy_begin_time",
            type: "input",
            attrs: {
                name: gettext("开始时间"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "bk_alarm_shield_strategy_end_time",
            type: "input",
            attrs: {
                name: gettext("结束时间"),
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