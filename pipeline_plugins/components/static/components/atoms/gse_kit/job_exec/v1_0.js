(function () {
    $.atoms.gsekit_job_exec = [
        {
            tag_code: "gsekit_bk_env",
            type: "select",
            attrs: {
                name: gettext("环境类型"),
                placeholder: gettext("请选择环境类型"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ],
                items: [
                    {text: '测试', value: "1"},
                    {text: '体验', value: "2"},
                    {text: '正式', value: "3"},
                ]
            }
        },
        {
            tag_code: "gsekit_job_action_choices",
            type: "select",
            attrs: {
                name: gettext("执行命令"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ],
                items: [
                    {text: '启动(start)', value: 'start'},
                    {text: '停止(stop)', value: 'stop'},
                    {text: '重启(restart)', value: 'restart'},
                    {text: '重载(reload)', value: 'reload'},
                    {text: '强制停止(kill)', value: 'force_stop'},
                    {text: '托管(auto)', value: 'set_auto'},
                    {text: '取消托管(noauto)', value: 'unset_auto'},
                    {text: '生成配置(createcfg)', value: 'generate'},
                    {text: '下发配置(pushcfg)', value: 'release'}
                ]
            }
        },
        {
            tag_code: "gsekit_set",
            type: "input",
            attrs: {
                name: gettext("集群"),
                hookable: true,
                placeholder: gettext("集群"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "gsekit_module",
            type: "input",
            attrs: {
                name: gettext("模块"),
                hookable: true,
                placeholder: gettext("模块"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "gsekit_service_id",
            type: "input",
            attrs: {
                name: gettext("服务实例"),
                hookable: true,
                placeholder: gettext("服务实例"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "gsekit_process_name",
            type: "input",
            attrs: {
                name: gettext("进程"),
                hookable: true,
                placeholder: gettext("进程别名"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "gsekit_process_id",
            type: "input",
            attrs: {
                name: gettext("process_id"),
                hookable: true,
                placeholder: gettext("process_id"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            "type": "select",
            "attrs": {
                "name": "配置模版",
                "hookable": true,
                "validation": [],
                "default": "",
                "value": "",
                "multiple": true,
                "multiple_limit": 0,
                "clearable": true,
                "allowCreate": false,
                "remote": true,
                "remote_url": $.context.get('site_url') + 'pipeline/gsekit_get_config_template_list' + '/' + $.context.getBkBizId() + '/',
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                "hasGroup": false,
                "disabled": false,
                "placeholder": "如不指定，则默认下发全部配置",
                "empty_text": "当前项目下无可用配置模版"
            },
            "events": [
                {
                    source: "gsekit_job_action_choices",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "generate" || value === "release") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "gsekit_job_action_choices",
                    type: "init",
                    action: function (value) {
                        let self = this;
                        if (value === "generate" || value === "release") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
            ],
            "methods": {},
            "tag_code": "gsekit_config_template"
        }
    ]
})();
