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
                url: $.context.get('site_url') + 'pipeline/file_upload/' + $.context.get('project').id + '/',
                placeholder: gettext("文件名不能包含中文和特殊字符且大小不能超过2G"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {
                beforeUpload(file, fileList) {
                    // 解决csrftoken过期问题
                    this.$set(this.headers, "X-CSRFToken", getCookie(window.APP_CODE + "_csrftoken"))
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
                placeholder: gettext("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行符分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
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
