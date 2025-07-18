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
            tag_code: "job_local_files",
            type: "upload",
            attrs: {
                name: gettext("本地文件"),
                hookable: true,
                auto_upload: true,
                url: window.FILE_UPLOAD_ENTRY || $.context.get('site_url') + 'pipeline/file_upload/',
                placeholder: $.context.getProjectId() == '' ? gettext("公共流程在编辑状态下无法直接上传文件，请勾选为全局变量后，在新建任务的参数填写阶段上传") : gettext("文件不能包含空格,支持中文文件名,本地上传文件大小不能超过 5GB"),
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
                    // 文件名不允许包含空格
                    if(file.name.includes(" ")){
                        return show_msg('上传失败: 文件名不允许包含空格', 'error');
                    }
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
            tag_code: "job_across_biz",
            type: "radio",
            attrs: {
                name: gettext("是否允许跨业务"),
                hookable: true,
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")},
                ],
                default: false,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_target_ip_list",
            type: "textarea",
            attrs: {
                name: gettext("目标服务器"),
                placeholder: gettext("请输入IP 地址，多IP可用空格、换行分隔\n 非本业务IP请输入管控区域:IP，并确保已在作业平台添加白名单"),
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
                name: gettext("执行账号"),
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
                placeholder: gettext("请输入绝对路径"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
