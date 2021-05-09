(function () {
    $.atoms.all_biz_execute_job_plan = [
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
                pagination: true,
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
                            name: gettext("退出码"),
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
