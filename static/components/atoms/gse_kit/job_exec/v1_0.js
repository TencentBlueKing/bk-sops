(function () {
    $.atoms.gsekit_job_exec = [
        {
            tag_code: "gsekit_bk_env",
            type: "select",
            attrs: {
                name: gettext("环境类型"),
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
            tag_code: "gsekit_job_object_choices",
            type: "radio",
            attrs: {
                name: gettext("操作对象"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ],
                items: [
                    {name: 'CONFIGFILE', value: 'configfile'},
                    {name: 'PROCESS', value: 'process'},
                ]
            }
        },
        {
            tag_code: "gsekit_job_action_choices",
            type: "select",
            attrs: {
                name: gettext("操作类型"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ],
                items: [
                    {text: '生成', value: 'GENERATE'},
                    {text: '下发', value: 'RELEASE'},
                    {text: '启动', value: 'START'},
                    {text: '停止', value: 'STOP'},
                    {text: '重启', value: 'RESTART'},
                    {text: '重载', value: 'RELOAD'},
                    {text: '强制停止', value: 'FORCE_STOP'},
                    {text: '托管', value: 'SET_AUTO'},
                    {text: '取消托管', value: 'UNSET_AUTO'}
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
                name: gettext("进程实例ID"),
                hookable: true,
                placeholder: gettext("进程实例ID"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
