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
    $.atoms.monitor_alarm_shield_strategy = [
        {
            tag_code: "bk_alarm_shield_strategy",
            type: "select",
            attrs: {
                name: gettext("策略"),
                remote: true,
                multiple: true,
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
            tag_code: "bk_alarm_shield_begin_time",
            type: "input",
            attrs: {
                name: gettext("开始时间"),
                hookable: true,
                placeholder: "请输入`yyyy-MM-dd HH:mm:ss`格式，建议引用自定义日期时间类型变量",
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            let self = this;
                            if (!self.get_parent) {
                                return result;
                            }
                            let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                            if ((bk_alarm_time_type.value === '0' || bk_alarm_time_type.value === '2') && this.value.length === 0) {
                                result.result = false;
                                result.error_message = gettext("开始时间不可为空");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "bk_alarm_time_type",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === '0' || value === '2') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "bk_alarm_shield_begin_time",
                    type: "init",
                    action: function () {
                        let self = this;
                        let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                        if (bk_alarm_time_type.value === '0' || bk_alarm_time_type.value === '2') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "bk_alarm_shield_end_time",
            type: "input",
            attrs: {
                name: gettext("结束时间"),
                hookable: true,
                placeholder: "请输入`yyyy-MM-dd HH:mm:ss`格式，建议引用自定义日期时间类型变量",
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            let self = this;
                            if (!self.get_parent) {
                                return result;
                            }
                            let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                            if (bk_alarm_time_type.value === '0' && this.value.length === 0) {
                                result.result = false;
                                result.error_message = gettext("结束时间不可为空");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "bk_alarm_time_type",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === '0') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "bk_alarm_shield_end_time",
                    type: "init",
                    action: function () {
                        let self = this;
                        let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                        if (bk_alarm_time_type.value === '0') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "bk_alarm_shield_duration",
            type: "input",
            hide: true,
            attrs: {
                name: gettext("持续时间(分钟)"),
                placeholder: gettext("输入屏蔽的分钟数"),
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            let self = this;
                            if (!self.get_parent) {
                                return result;
                            }
                            let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                            if ((bk_alarm_time_type.value === '1' || bk_alarm_time_type.value === '2') && this.value.length === 0) {
                                result.result = false;
                                result.error_message = gettext("持续时间不可为空");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "bk_alarm_time_type",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === '1' || value === '2') {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                },
                {
                    source: "bk_alarm_shield_duration",
                    type: "init",
                    action: function () {
                        let self = this;
                        let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                        if (bk_alarm_time_type.value === '1' || bk_alarm_time_type.value === '2') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
    ]
})();
