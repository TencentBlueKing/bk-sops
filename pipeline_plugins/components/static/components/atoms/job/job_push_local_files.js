(function () {
    $.atoms.job_push_local_files = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_get_business_list/',
                remote_data_init: function (resp) {
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
            tag_code: "job_local_files",
            type: "upload",
            attrs: {
                name: gettext("本地文件"),
                hookable: true,
                auto_upload: true,
                url: window.FILE_UPLOAD_ENTRY || $.context.get('site_url') + 'pipeline/file_upload/',
                placeholder: $.context.getProjectId() == '' ? gettext("公共流程在编辑状态下无法直接上传文件，请勾选为全局变量后，在新建任务的参数填写阶段上传") : gettext("文件名不能包含中文和特殊字符且大小不能超过2G"),
                disabled: $.context.getProjectId() == '',
                validation: [
                    {
                        type: "required"
                    }
                ]
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
                    var file_num = fileList.length;
                    if (response.result) {
                        fileList[file_num - 1].tag = response.tag;
                    } else {
                        fileList.splice(file_num - 2, 1);
                        show_msg(response.message, 'error');
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
            tag_code: "job_target_ip_list",
            type: "textarea",
            attrs: {
                name: gettext("目标IP"),
                placeholder: gettext("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
                hookable: true
            }
        },
        {
            tag_code: "job_target_account",
            type: "input",
            attrs: {
                name: gettext("目标账户"),
                hookable: true
            }
        },
        {
            tag_code: "job_target_path",
            type: "input",
            attrs: {
                name: gettext("目标路径"),
                placeholder: gettext("请输入绝对路径"),
                hookable: true
            }
        }
    ]
})();
