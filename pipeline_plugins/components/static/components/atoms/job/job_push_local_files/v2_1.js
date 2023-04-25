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

    $.atoms.job_push_local_files = [
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
            tag_code: "job_local_files_info",
            type: "combine",
            attrs: {
                hookable: true,
                name: gettext("上传文件"),
                children: [
                    {
                        tag_code: "job_local_files",
                        type: "upload",
                        attrs: {
                            name: gettext("本地文件"),
                            hookable: true,
                            auto_upload: true,
                            multiple: true,
                            url: window.FILE_UPLOAD_ENTRY || $.context.get('site_url') + 'pipeline/file_upload/',
                            placeholder: $.context.getProjectId() == '' ? gettext("公共流程在编辑状态下无法直接上传文件，请勾选为全局变量后，在新建任务的参数填写阶段上传") : gettext("文件不能包含空格,支持中文文件名,本地上传文件大小不能超过 5GB"),
                            disabled: $.context.getProjectId() == '',
                            validation: []
                        },
                        methods: {
                            beforeUpload(file, fileList) {
                                this.$set(this.headers, "X-CSRFToken", getCookie(window.APP_CODE + "_csrftoken"))
                                this.$set(this.headers, "APP-ProjectId", $.context.getProjectId())

                                var $this = this
                                $.ajax({
                                    url: $.context.get('site_url') + 'pipeline/apply_upload_ticket/',
                                    type: 'GET',
                                    dataType: 'json',
                                    async: false,
                                    success: function (resp) {
                                        if (resp.result === false) {
                                            show_msg(resp.message, 'error');
                                        } else {
                                            $this.$set($this.headers, "Upload-Ticket", resp.data.ticket)
                                        }
                                    },
                                    error: function () {
                                        show_msg('request job detail error', 'error');
                                    }
                                })
                            },
                            handleSuccess: function (response, file, fileList) {
                                if (response.result === false) {
                                    show_msg(response.message, 'error');
                                    // 原地删除，需要从后往前遍历
                                    for (var i = fileList.length - 1; i >= 0; i--) {
                                        if (fileList["response"]["result"] === false) {
                                            fileList.splice(i, 1)
                                        }
                                    }
                                }
                                this._set_value(fileList)
                            },
                            handleError: function (err, file, fileList) {
                                var result = JSON.parse(err.message)
                                show_msg(result.message, 'error');
                            }
                        }
                    },
                    {
                        tag_code: "job_target_path",
                        type: "input",
                        attrs: {
                            name: gettext("目标路径"),
                            placeholder: gettext("请输入绝对路径"),
                            hookable: true,
                            validation: [],
                            cols: 10,
                        }
                    },

                    {
                        tag_code: "add_files",
                        type: "button",
                        attrs: {
                            hookable: false,
                            type: "primary",
                            title: gettext('添加'),
                            size: "normal",
                            margin: "50px",
                            cols: 1,
                            formViewHidden: true
                        },
                        events: [
                            {
                                source: "add_files",
                                type: "click",
                                action: function () {
                                    let local_files_obj = this.get_parent().get_child('job_local_files');

                                    let job_target_path_obj = this.get_parent().get_child('job_target_path');
                                    let table_obj = this.get_parent().get_child('job_push_multi_local_files_table');

                                    let local_files = local_files_obj._get_value();
                                    let job_target_path = job_target_path_obj._get_value();

                                    if (local_files.length === 0) {
                                        alert(gettext("请上传文件"))
                                        return
                                    }
                                    if (job_target_path === "") {
                                        alert(gettext("请填写目标路径"))
                                        return
                                    }

                                    let show_name = "";
                                    let show_md5 = "";
                                    $.each(local_files, function (i, v) {
                                        show_name += v.name + "\n"
                                        show_md5 += v.response.md5 + "\n"
                                    })
                                    show_name = show_name.slice(0, show_name.length - 1)
                                    show_md5 = show_md5.slice(0, show_md5.length - 1)

                                    table_obj._get_value().push({
                                        "show_file": show_name,
                                        "file_info": local_files,
                                        "target_path": job_target_path,
                                        "md5": show_md5
                                    })
                                    table_obj._set_value(table_obj._get_value())

                                    //reset info tag
                                    local_files_obj._set_value([])
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "job_push_multi_local_files_table",
                        type: "datatable",
                        attrs: {
                            name: gettext("待上传文件表单"),
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                            empty_text: gettext("无数据"),
                            deleteable: true,
                            editable: true,
                            rowEditable: false,
                            columns: [
                                {
                                    tag_code: "show_file",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("文件信息")
                                    }
                                },
                                {
                                    tag_code: "file_info",
                                    type: "text",
                                    attrs: {
                                        name: gettext(""),
                                        hidden: true,
                                    }
                                },
                                {
                                    tag_code: "target_path",
                                    type: "text",
                                    attrs: {
                                        name: gettext("目标路径"),
                                    }
                                },
                                {
                                    tag_code: "md5",
                                    type: "text",
                                    attrs: {
                                        name: gettext("文件MD5"),
                                    }
                                }
                            ],
                        }

                    }

                ]
            }
        },
        {
            tag_code: "job_target_ip_list",
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
            tag_code: "job_target_account",
            type: "select",
            attrs: {
                name: gettext("执行账号"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                allowCreate: true,
                hookable: true,
                remote_url: function () {
                    let url = $.context.get('site_url') + 'pipeline/get_job_account_list/' +  $.context.getBkBizId() + '/'
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