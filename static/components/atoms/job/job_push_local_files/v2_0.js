(function () {
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
                            url: window.FILE_UPLOAD_ENTRY || $.context.get('site_url') + 'pipeline/file_upload/',
                            placeholder: $.context.getProjectId() == '' ? gettext("公共流程在编辑状态下无法直接上传文件，请勾选为全局变量后，在新建任务的参数填写阶段上传") : gettext("文件名不能包含中文和特殊字符且大小不能超过2G"),
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
                            margin:"50px",
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

                                    if(local_files.length === 0){
                                        alert(gettext("请上传文件"))
                                        return
                                    }
                                    if(job_target_path === ""){
                                        alert(gettext("请填写目标路径"))
                                        return
                                    }

                                    let show_name = "";
                                    $.each(local_files, function (i, v) {
                                        show_name += v.name + ";"
                                    })

                                    table_obj._get_value().push({
                                        "show_file": show_name,
                                        "file_info": local_files,
                                        "target_path": job_target_path
                                    })
                                    table_obj._set_value(table_obj._get_value())

                                    //reset info tag
                                    local_files_obj._set_value([])
                                    job_target_path_obj._set_value("")

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
                            editable: false,
                            rowEditable: false,
                            columns: [
                                {
                                    tag_code: "show_file",
                                    type: "text",
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
                name: gettext("目标IP"),
                placeholder: gettext("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
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
            type: "input",
            attrs: {
                name: gettext("目标账户"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },

    ]
})();
