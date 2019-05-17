(function () {
    $.atoms.job_timing_task = [
        {
            tag_code: "job_timing_task_id",
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: false,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + $.context.biz_cc_id + '/',
                remote_data_init: function (resp) {
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
            tag_code: "job_timing_task_name",
            type: "input",
            attrs: {
                name: gettext("定时作业名称"),
                hookable: false,
                placeholder: gettext("请填写定时作业名称"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "job_timing_task_id",
                    type: "change",
                    action: function (value) {
                        var $this = this;
                        $.ajax({
                            url: $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + $.context.biz_cc_id + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                let text = resp.data.filter((item) => {
                                    return item.value === value
                                })[0]['text'];
                                $this._set_value(text + '_' + (new Date()).getTime());
                            },
                            error: function () {
                                $this._set_value('');
                            }
                        });
                    }
                }
            ]
        },
        {
            tag_code: "job_timing_global_var",
            type: "datatable",
            attrs: {
                name: gettext("全局变量"),
                hookable: true,
                empty_text: gettext("没选中作业模板或当前作业模板全局变量为空"),
                columns: [
                    {
                        tag_code: "name",
                        type: "text",
                        attrs: {
                            name: gettext("参数名称"),
                        }
                    },
                    {
                        tag_code: "type",
                        type: "text",
                        attrs: {
                            name: gettext("参数类型"),
                            hidden: true,
                        }
                    },
                    {
                        tag_code: "value",
                        type: "textarea",
                        attrs: {
                            name: gettext("参数值"),
                            editable: true
                        }
                    },
                    {
                        tag_code: "description",
                        type: "text",
                        attrs: {
                            name: gettext("描述")
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_timing_task_id",
                    type: "change",
                    action: function (value) {
                        var $this = this;
                        this.changeHook(false);
                        this.set_loading(true);
                        $.ajax({
                            url: $.context.site_url + 'pipeline/job_get_job_detail_by_biz/' + $.context.biz_cc_id + '/' + value + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                $this._set_value(resp.data.global_var);
                                $this.set_loading(false);
                            },
                            error: function () {
                                $this._set_value([]);
                                $this.set_loading(false);
                            }
                        });
                    }
                }
            ]
        },
        {
            tag_code: "job_timing_rule",
            type: "textarea",
            attrs: {
                name: gettext("定时规则"),
                hookable: false,
                placeholder: gettext("定时任务crontab的定时规则，新建时必填，修改时选填，各字段含义为：秒 分 时 日 月 周 年（可选），如: 0 0/5 * * * ? 表示每5分钟执行一次，0 0 12 * * ? 2015表示2015年每天中午12点触发"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_timing_status",
            type: "radio",
            attrs: {
                name: gettext("定时作业状态"),
                hookable: false,
                items: [
                    {value: 2, name: gettext("暂停")},
                    {value: 1, name: gettext("启动")},
                ],
                default: 2,
                validation: [
                    {
                        type: "required"
                    }
                ],
            }
        }
    ]
})();
