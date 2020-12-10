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
                    {text: '测试', value: 'TESTING'},
                    {text: '体验', value: 'EXPERIENCE'},
                    {text: '正式', value: 'FORMAL'},
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
                    {text: '启动(start)', value: 'START'},
                    {text: '停止(stop)', value: 'STOP'},
                    {text: '重启(restart)', value: 'RESTART'},
                    {text: '重载(reload)', value: 'RELOAD'},
                    {text: '强制停止(kill)', value: 'FORCE_STOP'},
                    {text: '托管(set_auto)', value: 'SET_AUTO'},
                    {text: '取消托管(unset_auto)', value: 'UNSET_AUTO'},
                    {text: '生成配置(create_cfg)', value: 'GENERATE'},
                    {text: '下发配置(push_cfg)', value: 'RELEASE'}
                ]
            }
        },
        {
            tag_code: "gsekit_set",
            type: "input",
            attrs: {
                name: gettext("集群"),
                hookable: true,
                placeholder: gettext("集群ID"),
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
                placeholder: gettext("模块ID"),
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
                name: gettext("服务实例ID"),
                hookable: true,
                placeholder: gettext("服务实例ID"),
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
            "name": "config_template",
            "hookable": true,
            "validation": [
            ],
            "default": "",
            "hidden": false,
            "value": "",
            "multiple": false,
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
            "placeholder": "config_template",
            "empty_text": "当前项目下无可用配置模版"
        },
        "events": [],
        "methods": {},
        "tag_code": "gsekit_config_template"
        }
    ]
})();
