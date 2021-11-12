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
    $.atoms.sleep_timer = [
        {
            tag_code: "bk_timing",
            type: "input",
            attrs: {
                name: gettext("定时时间"),
                placeholder: gettext("秒(1-8位有效数字) 或 时间(%Y-%m-%d %H:%M:%S)"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    },
                ]
            },
        },
        {
            tag_code: "force_check",
            type: "radio",
            attrs: {
                name: gettext("强制晚于当前时间"),
                hookable: true,
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")}
                ],
                default: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
