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
    function getScriptContent(language) {
        // {value: "1", name: "shell"},
        // {value: "2", name: "bat"},
        // {value: "3", name: "perl"},
        // {value: "4", name: "python"},
        // {value: "5", name: "powershell"}
        // bash
        if (language === "1") {
            return '#!/bin/bash\n' +
                '\n' +
                'anynowtime="date +\'%Y-%m-%d %H:%M:%S\'"\n' +
                'NOW="echo [\\`$anynowtime\\`][PID:$$]"\n' +
                '\n' +
                '##### 可在脚本开始运行时调用，打印当时的时间戳及PID。\n' +
                'function job_start\n' +
                '{\n' +
                '    echo "`eval $NOW` job_starts"\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。 \n' +
                'function job_success\n' +
                '{\n' +
                '    MSG="$*"\n' +
                '    echo "`eval $NOW` job_success:[$MSG]"\n' +
                '    exit 0\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。\n' +
                'function job_fail\n' +
                '{\n' +
                '    MSG="$*"\n' +
                '    echo "`eval $NOW` job_fail:[$MSG]"\n' +
                '    exit 1\n' +
                '}\n' +
                '\n' +
                'job_start\n' +
                '\n' +
                '###### 作业平台中执行脚本成功和失败的标准只取决于脚本最后一条执行语句的返回值\n' +
                '###### 如果返回值为0，则认为此脚本执行成功，如果非0，则认为脚本执行失败\n' +
                '###### 可在此处开始编写您的脚本逻辑代码\n' +
                '\n'
        } else if (language === "2") {
            return '@echo on\n' +
                'setlocal enabledelayedexpansion\n' +
                'call:job_start\n' +
                '\n' +
                'REM 作业平台中执行脚本成功和失败的标准只取决于脚本最后一条执行语句的返回值\n' +
                'REM 如果返回值为0，则认为此脚本执行成功，如果非0，则认为脚本执行失败\n' +
                'REM 可在此处开始编写您的脚本逻辑代码\n' +
                '\n' +
                '\n' +
                '\n' +
                'REM 函数定定义区域，不要把正文写到函数区下面 \n' +
                'goto:eof\n' +
                'REM 可在脚本开始运行时调用，打印当时的时间戳及PID。\n' +
                ':job_start\n' +
                '    set cu_time=[%date:~0,10% %time:~0,8%]\n' +
                '    for /F "skip=3 tokens=2" %%i in (\'tasklist /v /FI "IMAGENAME eq cmd.exe" /FI "STATUS eq Unknown"\') do (\n' +
                '        set pid=[PID:%%i]\n' +
                '        goto:break\n' +
                '    )\n' +
                '    :break\n' +
                '    echo %cu_time%%pid% job_start\n' +
                '    goto:eof\n' +
                '    \n' +
                'REM 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。 \n' +
                ':job_success\n' +
                '    set cu_time=[%date:~0,10% %time:~0,8%]\n' +
                '    for /F "skip=3 tokens=2" %%i in (\'tasklist /v /FI "IMAGENAME eq cmd.exe" /FI "STATUS eq Unknown"\') do (\n' +
                '        set pid=[PID:%%i]\n' +
                '        goto:break\n' +
                '    )\n' +
                '    :break\n' +
                '    echo %cu_time%%pid% job_success:[%*]\n' +
                '    exit 0\n' +
                '    \n' +
                'REM 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。\n' +
                ':job_fail\n' +
                '    set cu_time=[%date:~0,10% %time:~0,8%]\n' +
                '    for /F "skip=3 tokens=2" %%i in (\'tasklist /v /FI "IMAGENAME eq cmd.exe" /FI "STATUS eq Unknown"\') do (\n' +
                '        set pid=[PID:%%i]\n' +
                '        goto:break\n' +
                '    )\n' +
                '    :break\n' +
                '    echo %cu_time%%pid% job_fail:[%*]\n' +
                '    exit 1\n' +
                '\n' +
                'REM admin'
        } else if (language === "3") {
            return '#!/usr/bin/perl\n' +
                '\n' +
                'use strict;\n' +
                '\n' +
                'sub job_localtime {\n' +
                '    my @n = localtime();\n' +
                '    return sprintf("%04d-%02d-%02d %02d:%02d:%02d",$n[5]+1900,$n[4]+1,$n[3], $n[2], $n[1], $n[0] );\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本开始运行时调用，打印当时的时间戳及PID。\n' +
                'sub job_start {\n' +
                '    print "[",&job_localtime,"][PID:$$] job_start\\n";\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。 \n' +
                'sub job_success {\n' +
                '    print "[",&job_localtime,"][PID:$$] job_success:[@_]\\n";\n' +
                '    exit 0;\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。\n' +
                'sub job_fail {\n' +
                '    print "[",&job_localtime,"][PID:$$] job_fail:[@_]\\n";\n' +
                '    exit 1;\n' +
                '}\n' +
                '\n' +
                'job_start;\n' +
                '\n' +
                '###### iJobs中执行脚本成功和失败的标准只取决于脚本最后一条执行语句的返回值\n' +
                '###### 如果返回值为0，则认为此脚本执行成功，如果非0，则认为脚本执行失败\n' +
                '###### 可在此处开始编写您的脚本逻辑代码\n' +
                '\n'
        } else if (language === "4") {
            return '#!/usr/bin/env python\n' +
                '# -*- coding: utf8 -*-\n' +
                '\n' +
                'import datetime\n' +
                'import os\n' +
                'import sys\n' +
                '\n' +
                'def _now(format="%Y-%m-%d %H:%M:%S"):\n' +
                '    return datetime.datetime.now().strftime(format)\n' +
                '\n' +
                '##### 可在脚本开始运行时调用，打印当时的时间戳及PID。\n' +
                'def job_start():\n' +
                '    print("[%s][PID:%s] job_start" % (_now(), os.getpid()))\n' +
                '\n' +
                '##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。 \n' +
                'def job_success(msg):\n' +
                '    print("[%s][PID:%s] job_success:[%s]" % (_now(), os.getpid(), msg))\n' +
                '    sys.exit(0)\n' +
                '\n' +
                '##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。\n' +
                'def job_fail(msg):\n' +
                '    print("[%s][PID:%s] job_fail:[%s]" % (_now(), os.getpid(), msg))\n' +
                '    sys.exit(1)\n' +
                '\n' +
                'if __name__ == \'__main__\':\n' +
                '\n' +
                '    job_start()\n' +
                '\n' +
                '###### iJobs中执行脚本成功和失败的标准只取决于脚本最后一条执行语句的返回值\n' +
                '###### 如果返回值为0，则认为此脚本执行成功，如果非0，则认为脚本执行失败\n' +
                '###### 可在此处开始编写您的脚本逻辑代码\n' +
                '\n'
        } else if (language === "5") {
            return '##### 可在脚本开始运行时调用，打印当时的时间戳及PID。\n' +
                'function job_start\n' +
                '{\n' +
                '    $cu_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"    \n' +
                '    "[{0}][PID:{1}] job_start1" -f $cu_date,$pid\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。 \n' +
                'function job_success\n' +
                '{\n' +
                '    $cu_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"\n' +
                '    if($args.count -ne 0)\n' +
                '    {\n' +
                '        $args | foreach {$arg_str=$arg_str + " " + $_}\n' +
                '        "[{0}][PID:{1}] job_success:[{2}]" -f $cu_date,$pid,$arg_str.TrimStart(\' \')\n' +
                '    }\n' +
                '    else\n' +
                '    {\n' +
                '        "[{0}][PID:{1}] job_success:[]" -f $cu_date,$pid\n' +
                '    }\n' +
                '    exit 0\n' +
                '}\n' +
                '\n' +
                '##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。\n' +
                'function job_fail\n' +
                '{\n' +
                '    $cu_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"\n' +
                '    if($args.count -ne 0)\n' +
                '    {\n' +
                '        $args | foreach {$arg_str=$arg_str + " " + $_}\n' +
                '        "[{0}][PID:{1}] job_fail:[{2}]" -f $cu_date,$pid,$arg_str.TrimStart(\' \')\n' +
                '    }\n' +
                '    else\n' +
                '    {\n' +
                '        "[{0}][PID:{1}] job_fail:[]" -f $cu_date,$pid\n' +
                '    }\n' +
                '    exit 1\n' +
                '}\n' +
                '\n' +
                'job_start\n' +
                '\n' +
                '###### 作业平台中执行脚本成功和失败的标准只取决于脚本最后一条执行语句的返回值\n' +
                '###### 如果返回值为0，则认为此脚本执行成功，如果非0，则认为脚本执行失败\n' +
                '###### 可在此处开始编写您的脚本逻辑代码\n' +
                '\n'
        }
        return ""
    }


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

    $.atoms.job_fast_execute_script = [
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
            tag_code: "job_script_source",
            type: "radio",
            attrs: {
                name: gettext("脚本来源"),
                hookable: false,
                items: [
                    {value: "manual", name: gettext("手工录入")},
                    {value: "general", name: gettext("业务脚本")},
                    {value: "public", name: gettext("公共脚本")},
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
                    source: "job_script_source",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "job_script_type",
            type: "radio",
            attrs: {
                name: gettext("脚本类型"),
                hookable: true,
                items: [
                    {value: "1", name: "shell"},
                    {value: "2", name: "bat"},
                    {value: "3", name: "perl"},
                    {value: "4", name: "python"},
                    {value: "5", name: "powershell"}
                ],
                default: "1",
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            var self = this;
                            var result = {
                                result: true,
                                error_message: ""
                            }
                            if (!self.get_parent) {
                                return result;
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "manual" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请选择脚本类型");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请选择脚本类型");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_script_source",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "manual") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "job_content",
            type: "code_editor",
            attrs: {
                name: gettext("脚本内容"),
                hookable: true,
                placeholder: gettext("填写执行脚本内容"),
                language: "shell",
                default: getScriptContent("1"),
                showLanguageSwitch: false,
                height: "400px",
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            var self = this;
                            var result = {
                                result: true,
                                error_message: ""
                            }
                            if (!self.get_parent) {
                                return result;
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "manual" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请输入脚本内容");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请输入脚本内容");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_script_type",
                    type: "change",
                    action: function (value) {
                        let content = getScriptContent(value)
                        this.value = content
                    }
                },
                {
                    source: "job_script_source",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "manual") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "job_script_list_public",
            type: "select",
            attrs: {
                name: gettext("脚本列表"),
                hookable: true,
                remote: true,
                remote_url: function () {
                    return $.context.get('site_url') + 'pipeline/job_get_public_script_name_list/';
                },
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            var self = this;
                            var result = {
                                result: true,
                                error_message: ""
                            };
                            if (!self.get_parent) {
                                return result;
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "public" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请选择脚本");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请选择脚本");
                            }
                            return result;
                        }
                    }
                ],
            },
            events: [
                {
                    source: "job_script_source",
                    type: "change",
                    action: function (value) {
                        var self = this
                        if (value === "public") {
                            self.show()
                        } else {
                            self.hide()
                        }
                    }
                }
            ]
        },
        {
            tag_code: "job_script_list_general",
            type: "select",
            attrs: {
                name: gettext("脚本列表"),
                hookable: true,
                remote: true,
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/job_get_script_name_list/' + $.context.getBkBizId() + '/?type=general';
                    return url;
                },
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
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
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "general" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请选择脚本");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请选择脚本");
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        if (cc_id !== '' && $.context.canSelectBiz()) {
                            this.remote_url = $.context.get('site_url') + 'pipeline/job_get_script_name_list/' + cc_id + '/?type=general';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if (!$.context.canSelectBiz()) {
                            return;
                        }
                        this._set_value('');
                        if (value === '') {
                            return;
                        }
                        this.remote_url = $.context.get('site_url') + 'pipeline/job_get_script_name_list/' + value + '/?type=general';
                        this.remoteMethod();
                    }
                },
                {
                    source: "job_script_source",
                    type: "change",
                    action: function (value) {
                        var self = this
                        if (value === "general") {
                            self.show()
                        } else {
                            self.hide()
                        }
                    }
                }
            ]
        },
        {
            tag_code: "job_script_param",
            type: "input",
            attrs: {
                name: gettext("脚本参数"),
                placeholder: gettext("可为空, 脚本执行时传入的参数，同脚本在终端执行时的传参格式， 如:./test.sh xxxx xxx xxx"),
                hookable: true
            },
        },
        {
            tag_code: "job_script_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒(1 - 86400)，为空时使用 JOB 默认值"),
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
                ],
            },
        },
        {
            tag_code: "job_account",
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
                            hookable: false,
                            tips: "<p>.&nbsp;每个批次支持用整数、百分比(n%)和算式(+n,&nbsp;*n)，以空格分隔</p>\n" +
                                "\n</br>" +
                                "<p>.&nbsp;使用算式&nbsp;(+n,&nbsp;*n)&nbsp;时，前一个批次必须是整数（如：2&nbsp;*2）</p>\n" +
                                "\n</br>" +
                                "<p>.&nbsp;百分比取值遇小数点时会向上取整，100%代表取全量服务器（100%&nbsp;只允许出现在末位）</p>",
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
        },
        {
            tag_code: "job_success_id",
            type: "select",
            attrs: {
                name: gettext("JOB成功历史"),
                allowCreate: true,
                hookable: false,
                remote: true,
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/jobv3_get_instance_list/' + $.context.getBkBizId() + '/1/3/';
                    return url;
                },
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                showRightBtn: true,
                rightBtnCb: function () {
                    if (!this.value) {
                        return;
                    }
                    let biz_cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                    let bk_job_host = window.BK_JOB_HOST;
                    if (bk_job_host.charAt(bk_job_host.length - 1) == "/") bk_job_host = bk_job_host.substr(0, bk_job_host.length - 1);
                    let url = bk_job_host + '/' + biz_cc_id + "/execute/task/" + this.value;
                    window.open(url, '_blank')
                },
                cols: 10
            },
            events: [
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        if ($.context.exec_env === "NODE_CONFIG") {
                            this.hide()
                        }
                        if ($.context.exec_env === "NODE_EXEC_DETAIL") {
                            if (!this.value) {
                                this.hide()
                                return
                            }
                        }
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        if (cc_id !== '' && $.context.canSelectBiz()) {
                            this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_instance_list/' + cc_id + '/1/3/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "button_refresh_2",
                    type: "click",
                    action: function (value) {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_instance_list/' + cc_id + '/1/3/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if (!$.context.canSelectBiz()) {
                            return;
                        }
                        this._set_value('');
                        if (value === '') {
                            return;
                        }
                        this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_instance_list/' + value + '/1/3/';
                        this.remoteMethod();
                    }
                }
            ]
        },
        {
            tag_code: "©",
            type: "button",
            attrs: {
                hookable: false,
                type: "primary",
                title: '刷新',
                size: "normal",
                cols: 1,
                formViewHidden: true
            },
            events: [
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        if ($.context.exec_env === "NODE_CONFIG") {
                            this.hide()
                        }
                        if ($.context.exec_env === "NODE_EXEC_DETAIL") {
                            if (!this.value) {
                                this.hide()
                                return
                            }
                        }
                    }
                },
            ]
        },
    ]
})();