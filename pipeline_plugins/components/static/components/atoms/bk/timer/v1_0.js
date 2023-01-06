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
(function() {
    $.atoms.sleep_timer = [
        {
            tag_code: "timing_settings",
            type: "combine",
            attrs: {
                name: gettext("定时设置"),
                hookable: true,
                children: [
                    {
                        tag_code: "timing_mode",
                        type: "radio",
                        attrs: {
                            name: gettext("定时模式"),
                            items: [
                                {value: "seconds", name: gettext("等待N秒后执行")},
                                {value: "specific_time", name: gettext("指定时间执行")}
                            ],
                            default: "seconds",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                    },
                    {
                        tag_code: "timing_seconds",
                        type: "input",
                        attrs: {
                            name: gettext("等待时间")
                        },
                        events: [
                            {
                                source: "timing_mode",
                                type: "init",
                                action: function(value) {
                                    let self = this;
                                    if (value !== "seconds") {
                                        self.hide();
                                    } else {
                                        self.show();
                                    }
                                }
                            },
                            {
                                source: "timing_mode",
                                type: "change",
                                action: function(value) {
                                    let self = this;
                                    if (value !== "seconds") {
                                        self.hide();
                                    } else {
                                        self.show();
                                    }
                                }
                            }

                        ]
                    },
                    {
                        tag_code: "timing_specific_time",
                        type: "datetime",
                        attrs: {
                            name: gettext("日期时间"),
                        },
                        events: [
                            {
                                source: "timing_mode",
                                type: "init",
                                action: function(value) {
                                    let self = this;
                                    if (value !== "specific_time") {
                                        self.hide();
                                    } else {
                                        self.show();
                                    }
                                }
                            },
                            {
                                source: "timing_mode",
                                type: "change",
                                action: function(value) {
                                    let self = this;
                                    if (value !== "specific_time") {
                                        self.hide();
                                    } else {
                                        self.show();
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
    ]
})();
