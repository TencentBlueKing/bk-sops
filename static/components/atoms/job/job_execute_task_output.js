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
    $.atoms.job_execute_task = [
        {
            tag_code: "job_id",
            type: "text",
            attrs: {
                name: gettext("JOB 任务 ID"),
                value: $.context.getOutput("job_inst_id")
            }
        },
        {
            tag_code: "job_url",
            type: "text",
            attrs: {
                name: gettext("JOB 任务链接"),
                value: $.context.getOutput("job_inst_url")
            }
        },
        {
            tag_code: "job_task_ip_exit_codes",
            type: "datatable",
            attrs: {
                name: gettext("IP 执行状态"),
                editable: false,
                columns: [
                    {
                        tag_code: "ip",
                        type: "text",
                        attrs: {
                            name: "IP",
                        }
                    },
                    {
                        tag_code: "exit_code",
                        type: "text",
                        attrs: {
                            name: "退出码",
                        }
                    },
                ]
            }
        },
        {
            tag_code: "job_task_ip_list",
            type: "select",
            attrs: {
                name: gettext("执行 IP 列表"),
                remote_data_init: function (resp) {
                    var ipList = resp.data.map(x => function (x) {
                        var item = new Object()
                        item.text = x.ip
                        item.value = x.ip
                        return item
                    }(x))
                    
                    var ipExitCodeList = resp.data.map(x => function () {
                        var item = new Object()
                        item.ip = x.ip
                        item.exit_code = x.exit_code
                        return item
                    }(x))
                    var ipTable = this.get_parent().get_child('job_task_ip_exit_codes')
                    ipTable._set_value(ipExitCodeList)
                    
                    this.logDict = {}
                    for (i in resp.data) {
                        this.logDict[resp.data[i].ip] = resp.data[i].log
                    }

                    return ipList
                },
                remote_url: $.context.get("site_url") + "pipeline/job_get_instance_detail/" + ($.context.getInput("bk_biz_id") || $.context.getBkBizId()) + "/" + $.context.getOutput("job_inst_id") + "/"
            }
        },
        {
            tag_code: "job_log",
            type: "log_display",
            attrs: {
                name: gettext("作业日志"),
                value: ""
            },
            events: [
                {
                    source: "job_task_ip_list",
                    type: "change",
                    action: function (value) {
                        var logs = this.get_parent().get_child('job_task_ip_list').logDict[value]
                        this._set_value(logs)
                    }
                }
            ]
        }
    ]

})();