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


    $.atoms.job_local_content_upload = [
        {
            tag_code: "local_name",
            type: "input",
            attrs: {
                name: gettext("生成文件名[后缀]"),
                placeholder: gettext("输入生成文件名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "local_content",
            type: "textarea",
            attrs: {
                name: gettext("文本内容"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_ip_list",
            type: "textarea",
            attrs: {
                name: gettext("目标服务器"),
                placeholder: gettext("请输入IP 地址，多IP可用空格、换行分隔\n 非本业务IP请输入云区域:IP，并确保已在作业平台添加白名单"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "file_account",
            type: "select",
            attrs: {
                name: gettext("执行账号"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                allowCreate: true,
                hookable: true,
                remote_url: function () {
                    let url = $.context.get('site_url') + 'pipeline/get_job_account_list/' + $.context.getBkBizId() + '/'
                    return url
                },
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
            }
        },
        {
            tag_code: "file_path",
            type: "input",
            attrs: {
                name: gettext("目标路径"),
                placeholder: gettext("输入目标路径"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "job_rolling_config",
            type: "combine",
            attrs: {
                name: "滚动执行配置",
                hookable: true,
                children: [
                    {
                        tag_code: "job_rolling_execute",
                        type: "checkbox",
                        attrs: {
                            name: gettext("滚动执行"),
                            hookable: false,
                            tips: "<p>启动滚动执行后，目标服务器将按策略规则分批次串行执行（而非全量并行）</p>",
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
                            placeholder: gettext("详情请查看JOB使用指引"),
                            hookable: false,
                            tips: "<p>·&nbsp;每个占位以空格分隔<br>\n" +
                                "·&nbsp;支持n、n%、*n、+n&nbsp;，且&nbsp;n&nbsp;只能为整数<br>\n" +
                                "·&nbsp;+和*运算符只能在最末位，100%代表全部服务器<br>\n" +
                                "·&nbsp;-&nbsp;n&nbsp;代表具体多少台<br>\n" +
                                "·&nbsp;n%&nbsp;代表总量的百分之n台（遇小数点则向上取整）<br>\n" +
                                "·&nbsp;+n&nbsp;代表每次在前一批数量的基础上增加n台<br>\n" +
                                "·&nbsp;*n&nbsp;代表每次在前一批数量的基础上乘于n台</p>",
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
                                {text: '默认（执行失败则暂停）', value: 1},
                                {text: '忽略失败，自动滚动下一批', value: 2},
                                {text: '不自动，每批次都人工确认', value: 3},
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