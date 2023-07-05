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
                            var self = this
                            var result = {
                                result: true,
                                error_message: ""
                            }
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "manual" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请选择脚本类型");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请选择脚本类型");
                            }
                            return result
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
                            self.show()
                        } else {
                            self.hide()
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
                variable_render: false,
                placeholder: gettext("填写执行脚本内容"),
                language: "shell",
                default: getScriptContent("1"),
                showLanguageSwitch: false,
                height: "400px",
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            var self = this
                            var result = {
                                result: true,
                                error_message: ""
                            }
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "manual" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请输入脚本内容");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请输入脚本内容");
                            }
                            return result
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
                            self.show()
                        } else {
                            self.hide()
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
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/job_get_script_list/' + $.context.getBkBizId() + '/?type=public&value_field=online_script_version_id';
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
                            var self = this;
                            var result = {
                                result: true,
                                error_message: ""
                            };
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('job_script_source')) {
                                if (self.get_parent().get_child('job_script_source').value === "public" && !value) {
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
                ],
            },
            events: [
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        if (cc_id !== '' && $.context.canSelectBiz()) {
                            this.remote_url = $.context.get('site_url') + 'pipeline/job_get_script_list/' + cc_id + '/?type=public&value_field=online_script_version_id';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if (!$.context.canSelectBiz() || value === '') {
                            return;
                        }
                        this.remote_url = $.context.get('site_url') + 'pipeline/job_get_script_list/' + value + '/?type=public&value_field=online_script_version_id';
                        this.remoteMethod();
                    }
                },
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
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/job_get_script_list/' + $.context.getBkBizId() + '/?type=general&value_field=online_script_version_id';
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
                            this.remote_url = $.context.get('site_url') + 'pipeline/job_get_script_list/' + cc_id + '/?type=general&value_field=online_script_version_id';
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
                        this.remote_url = $.context.get('site_url') + 'pipeline/job_get_script_list/' + value + '/?type=general&value_field=online_script_version_id';
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
            tag_code: "job_script_name",
            type: "text",
            attrs: {
                name: gettext("脚本名称"),
                hookable: false,
            },
            events: [
                {
                    source: "job_script_name",
                    type: "init",
                    action: function (value) {
                        this.hide();
                        if (!this.get_parent || !this.get_parent().get_child('job_script_list_general')._get_value() || this.get_parent().get_child("job_script_source")._get_value() !== "general") {
                            return;
                        }
                        var self = this;
                        const script_version = this.get_parent().get_child('job_script_list_general')._get_value();
                        const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/job_get_script_by_script_version/' + $.context.getBkBizId() + '/?script_version=' + script_version;
                        $.ajax({
                            url: url,
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                self._set_value(resp.data.script_name);
                                if (resp.data.script_name !== "") {
                                    self.show();
                                }
                            },
                            error: function () {
                                show_msg('request job script version detail error', 'error');
                            }
                        });
                    }
                },
                {
                    source: "job_script_list_general",
                    type: "change",
                    action: function (value) {
                        this.hide();
                    }
                },
                {
                    source: "job_script_source",
                    type: "change",
                    action: function (value) {
                        this.hide();
                    }
                },
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
                ]
            }
        },
        {
            tag_code: "job_account",
            type: "input",
            attrs: {
                name: gettext("执行账号"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "ip_is_exist",
            type: "radio",
            attrs: {
                name: gettext("IP 存在性校验"),
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")},
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
