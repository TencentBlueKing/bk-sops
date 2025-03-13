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

    var fixed = /^([1-9]\d*)$/;
    var fixedIn = /^\+([1-9]\d*)$/;
    var fixedMu = /^\*([1-9]\d*)$/;
    var per = /^([1-9]\d?)%$/;
    var all = /^100%$/;

    function validate_job_rolling_expression(exprStr) {
        debugger
        var batchStack = exprStr.trim().split(' ');
        if (batchStack.length < 1) {
            return '';
        }

        var lastFixedNum = 0;
        var lastPerNum = '';

        var lastBatchPre = batchStack.length > 1 ? '后面' : '';

        var translateSequence = (value) => {
            var batchTotal = value.length;

            var parse = (atoms, batchNum) => {
                var fixedData = atoms.match(fixed);
                if (fixedData) {
                    var fixedNum = parseInt(fixedData[1], 10);

                    lastPerNum = '';
                    lastFixedNum = fixedNum;

                    if (batchNum === batchTotal) {
                        return [`${lastBatchPre}按每${fixedNum}台一批直至结束`];
                    }
                    return [`第${batchNum}批${fixedNum}台`];
                }

                var perData = atoms.match(per);
                if (perData) {
                    var perNum = parseInt(perData[1], 10);

                    lastFixedNum = 0;
                    lastPerNum = perNum;

                    if (batchNum === batchTotal) {
                        return [`${lastBatchPre}按每${perNum}%台一批直至结束`];
                    }
                    return [`第${batchNum}批${perNum}%台`];
                }

                var fixedInData = atoms.match(fixedIn);
                if (fixedInData) {
                    if (batchNum === 1) {
                        throw new Error(`${atoms} 不能出现在开头`);
                    }
                    if (batchNum < batchTotal) {
                        throw new Error(`${atoms} 必须出现在最后一位`);
                    }

                    var step = parseInt(fixedInData[1], 10);

                    var textQueue = [];
                    if (lastPerNum) {
                        textQueue.push(`第${batchNum}批${lastPerNum}%+${step}台`);
                        textQueue.push(`第${batchNum + 1}批${lastPerNum}%+${step + step}台`);
                    } else if (lastFixedNum) {
                        textQueue.push(`第${batchNum}批${step + lastFixedNum}台`);
                        textQueue.push(`第${batchNum + 1}批${step + step + lastFixedNum}台`);
                    }
                    textQueue.push(`...之后“每批增加${step}”台直至结束`);
                    return textQueue;
                }

                var fixedMuData = atoms.match(fixedMu);
                if (fixedMuData) {
                    if (batchNum === 1) {
                        throw new Error(`${atoms} 不能出现在开头`);
                    }
                    if (batchNum < batchTotal) {
                        throw new Error(`${atoms} 必须出现在最后一位`);
                    }

                    var rate = parseInt(fixedMuData[1], 10);
                    var textQueue = [];
                    if (lastPerNum) {
                        textQueue.push(`第${batchNum}批${rate * lastPerNum}%台`);
                        textQueue.push(`第${batchNum + 1}批${rate * rate * lastPerNum}%台`);
                    } else if (lastFixedNum) {
                        textQueue.push(`第${batchNum}批${rate * lastFixedNum}台`);
                        textQueue.push(`第${batchNum + 1}批${rate * rate * lastFixedNum}台`);
                    }
                    textQueue.push(`...之后“每批乘于${rate}”台直至结束`);
                    return textQueue;
                }

                if (all.test(atoms)) {
                    if (batchNum < batchTotal) {
                        throw new Error(`${atoms} 必须出现在最后一位`);
                    }
                    if (batchNum === 1) {
                        return ['全部执行'];
                    }

                    return [`第${batchNum}批执行所有剩余主机`];
                }

                throw new Error(`不支持的配置规则 ${atoms}`);
            };
            var result = [];
            value.forEach((atoms, index) => {
                result.push.apply(result, parse(atoms, index + 1));
            });
            return result.join('，');
        };

        return translateSequence(batchStack);
    }

    $.atoms.job_fast_push_file = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                allowCreate: true,
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_get_business_list/',
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                disabled: !$.context.canSelectBiz(),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {
                _tag_init: function () {
                    if (this.value) {
                        return
                    }
                    this._set_value($.context.getBkBizId())
                }
            }
        },
        {
            tag_code: "job_source_files_origin",
            type: "radio",
            attrs: {
                name: gettext("源文件来源"),
                hookable: false,
                items: [
                    {value: "server", name: gettext("服务器")},
                    {value: "file_source", name: gettext("文件源")},
                ],
                default: "server",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "job_source_files_origin",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "job_server",
            type: "datatable",
            attrs: {
                name: gettext("服务器"),
                editable: true,
                add_btn: true,
                columns: [
                    {
                        tag_code: "ip",
                        type: "input",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("【IP】"),
                            width: '170px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "files",
                        type: "textarea",
                        attrs: {
                            name: gettext("文件路径"),
                            placeholder: gettext("多个用换行分隔"),
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "account",
                        type: "input",
                        attrs: {
                            name: gettext("执行账户"),
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
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            if (!value) {
                                result.result = false;
                                result.error_message = gettext("服务器不能为空")
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_source_files_origin",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "server") {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                }
            ],
        },
        {
            tag_code: "job_source_files",
            type: "datatable",
            attrs: {
                name: gettext("源文件"),
                editable: true,
                add_btn: true,
                columns: [
                    {
                        tag_code: "file_source",
                        type: "input",
                        attrs: {
                            name: gettext("文件源"),
                            placeholder: gettext("请选择文件源"),
                            width: '170px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "files",
                        type: "textarea",
                        attrs: {
                            name: gettext("文件路径"),
                            placeholder: gettext("请输入源文件在文件源中的完整路径，多个路径请选择一种分隔符进行分隔，支持换行或逗号"),
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
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            if (!value) {
                                result.result = false;
                                result.error_message = gettext("源文件不能为空")
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_source_files_origin",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "file_source") {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "upload_speed_limit",
            type: "input",
            attrs: {
                name: gettext("上传限速"),
                placeholder: gettext("MB/s 若不限速则不填写"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            if (!value) {
                                return result
                            }
                            var reg = /^[\d]+$/;
                            if (!reg.test(value)) {
                                result.result = false;
                                result.error_message = gettext("上传限速必须为整数")
                            }
                            return result
                        }
                    }
                ]
            }
        },
        {
            tag_code: "download_speed_limit",
            type: "input",
            attrs: {
                name: gettext("下载限速"),
                placeholder: gettext("MB/s 若不限速则不填写"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            if (!value) {
                                return result
                            }
                            var reg = /^[\d]+$/;
                            if (!reg.test(value)) {
                                result.result = false;
                                result.error_message = gettext("下载限速必须为整数")
                            }
                            return result
                        }
                    }
                ]
            }
        },
        {
            tag_code: "select_method",
            type: "radio",
            attrs: {
                name: gettext("填参方式"),
                hookable: false,
                items: [
                    {value: "manual", name: gettext("手动填写")},
                    {value: "auto", name: gettext("单行自动扩展")},
                ],
                default: "manual",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "select_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "job_dispatch_attr",
            type: "datatable",
            attrs: {
                name: gettext("分发配置"),
                add_btn: true,
                hookable: true,
                columns: [
                    {
                        tag_code: "job_ip_list",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("IP必须填写【管控区域ID:IP】或者【IP】格式之一"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "job_target_path",
                        type: "input",
                        attrs: {
                            name: gettext("目标路径"),
                            placeholder: gettext("请输入绝对路径（可用[FILESRCIP]代替源IP）"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "job_account",
                        type: "input",
                        attrs: {
                            name: gettext("执行账户"),
                            placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                ],
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [],
            methods: {
                _tag_init: function () {
                    if (this.value) {
                        return
                    }
                    this._set_value($.context.getBkBizId())
                }
            }
        },
        {
            tag_code: "break_line",
            type: "input",
            attrs: {
                name: gettext("自动扩展分隔符"),
                placeholder: gettext("可为空，单行自动扩展模式下每一行的换行符，默认使用 ,"),
                hookable: true
            },
            events: [
                {
                    source: "select_method",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "auto") {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                }
            ],
        },
        {
            tag_code: "job_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒(1 - 86400)，为空时使用JOB默认值"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            if (!value) {
                                return result
                            }
                            var reg = /^[\d]+$/;
                            if (!reg.test(value)) {
                                result.result = false;
                                result.error_message = gettext("超时时间必须为整数")
                            }
                            if (+value < 1 || +value > 86400) {
                                result.result = false;
                                result.error_message = gettext("超时时间必须在 1 - 86400 范围内")
                            }
                            return result
                        }
                    }
                ]
            }
        },
        {
            tag_code: "job_rolling_config",
            type: "combine",
            attrs: {
                name: gettext("滚动执行配置"),
                hookable: true,
                children: [
                    {
                        tag_code: "job_rolling_execute",
                        type: "checkbox",
                        attrs: {
                            name: gettext("滚动执行"),
                            hookable: false,
                            tips: gettext("<p>启动滚动执行后，目标服务器将按策略规则分批次串行执行（而非全量并行）</p>"),
                            items: [
                                {name: gettext(""), value: "open"},
                            ],
                            validation: []
                        }
                    },
                    {
                        tag_code: "job_rolling_expression",
                        type: "input",
                        attrs: {
                            name: gettext("滚动策略"),
                            hookable: false,
                            tips: gettext("<p>.&nbsp;每个批次支持用整数、百分比(n%)和算式(+n,&nbsp;*n)，以空格分隔</p>\n" +
                                "\n</br>" +
                                "<p>.&nbsp;使用算式&nbsp;(+n,&nbsp;*n)&nbsp;时，前一个批次必须是整数（如：2&nbsp;*2）</p>\n" +
                                "\n</br>" +
                                "<p>.&nbsp;百分比取值遇小数点时会向上取整，100%代表取全量服务器（100%&nbsp;只允许出现在末位）</p>"),
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let self = this
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        }
                                        if (!self.get_parent) {
                                            return result
                                        } else if (self.get_parent().get_child('job_rolling_execute')) {
                                            if (self.get_parent().get_child('job_rolling_execute').value.includes("open") && !value.toString()) {
                                                result.result = false;
                                                result.error_message = gettext("滚动执行开启时滚动策略为必填项");
                                            }
                                        }
                                        if (value) {
                                            try {
                                                validate_job_rolling_expression(value)
                                            } catch (err) {
                                                result.result = false;
                                                result.error_message = err.message;
                                            }
                                        }
                                        return result
                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "job_rolling_execute",
                                type: "change",
                                action: function (value) {
                                    var self = this
                                    if (value.includes("open")) {
                                        self.show()
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "job_rolling_execute",
                                type: "init",
                                action: function () {
                                    const job_rolling_execute = this.get_parent && this.get_parent().get_child('job_rolling_execute')._get_value();
                                    if (job_rolling_execute.includes("open")) {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "job_rolling_mode",
                        type: "select",
                        attrs: {
                            name: gettext("滚动机制"),
                            hookable: false,
                            default: 1,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let self = this
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        }
                                        if (!self.get_parent) {
                                            return result
                                        } else if (self.get_parent().get_child('job_rolling_execute')) {
                                            if (self.get_parent().get_child('job_rolling_execute').value.includes("open") && !value.toString()) {
                                                result.result = false;
                                                result.error_message = gettext("滚动执行开启时滚动机制为必填项");
                                            }
                                        }
                                        return result
                                    }
                                }
                            ],
                            items: [
                                {text: gettext('默认（执行失败则暂停）'), value: 1},
                                {text: gettext('忽略失败，自动滚动下一批'), value: 2},
                                {text: gettext('不自动，每批次都人工确认'), value: 3},
                            ]
                        },
                        events: [
                            {
                                source: "job_rolling_execute",
                                type: "change",
                                action: function (value) {
                                    var self = this
                                    if (value.includes("open")) {
                                        self.show()
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "job_rolling_execute",
                                type: "init",
                                action: function () {
                                    const job_rolling_execute = this.get_parent && this.get_parent().get_child('job_rolling_execute')._get_value();
                                    if (job_rolling_execute.includes("open")) {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                        ]
                    },
                ]
            }
        }
    ]
})();
