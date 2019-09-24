(function(){
    $.atoms.nodeman_create_task = [
        {
            tag_code: "nodeman_bk_biz_id",
            type: "input",
            attrs: {
                name: gettext("业务ID"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "nodeman_bk_cloud_id",
            type: "input",
            attrs: {
                name: gettext("云区域ID"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "nodeman_node_type",
            type: "radio",
            attrs: {
                name: gettext("主机节点类型"),
                hookable: true,
                items: [
                    {value: "AGENT", name: gettext("AGENT")},
                    {value: "PROXY", name: gettext("PROXY")},
                    {value: "PAGENT", name: gettext("PAGENT")}
                ],
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "nodeman_op_type",
                type: "select",
                attrs: {
                    name: gettext("操作类型"),
                    width: '100px',
                    items: [
                        {value: "INSTALL", text: gettext("安裝")},
                        {value: "REINSTALL", text: gettext("重新安装")},
                        {value: "UNINSTALL", text: gettext("卸载")},
                        {value: "REMOVE", text: gettext("移除")},
                        {value: "UPGRADE", text: gettext("升级")},
                    ],
                    editable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
        },
        {
            tag_code: "nodeman_hosts",
            type: "datatable",
            attrs: {
                name: gettext("主机相关信息"),
                editable: true,
                add_btn: true,
                columns: [
                    {
                        tag_code: "conn_ips",
                        type: "input",
                        attrs: {
                            name: gettext("主机通信IP"),
                            placeholder: gettext("多个用英文逗号隔开"),
                            width: '100px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "login_ip",
                        type: "input",
                        attrs: {
                            name: gettext("主机登陆IP"),
                            placeholder: gettext("适配复杂网络时填写"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "data_ip",
                        type: "input",
                        attrs: {
                            name: gettext("主机数据IP"),
                            placeholder: gettext("适配复杂网络时填写"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "cascade_ip",
                        type: "input",
                        attrs: {
                            name: gettext("级联IP"),
                            placeholder: gettext("安装Proxy时必填"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "os_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作系统类型"),
                            width: '100px',
                            items: [
                                {value: "LINUX", text: gettext("LINUX")},
                                {value: "WINDOWS", text: gettext("WINDOWS")},
                                {value: "AIX", text: gettext("AIX")}
                            ],
                            editable: true
                        }
                    },
                    {
                        tag_code: "has_cygwin",
                        type: "select",
                        attrs: {
                            name: gettext("是否安装cygwin"),
                            items: [
                                {value: "1", text: gettext("是")},
                                {value: "0", text: gettext("否")},
                            ],
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "port",
                        type: "input",
                        attrs: {
                            name: gettext("端口号"),
                            width: '100px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "account",
                        type: "input",
                        attrs: {
                            name: gettext("登陆账号"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "auth_type",
                        type: "select",
                        attrs: {
                            name: gettext("认证方式"),
                            width: '100px',
                            editable: true,
                            items: [
                                {value: "PASSWORD", text: gettext("PASSWORD")},
                                {value: "KEY", text: gettext("KEY")}
                            ],
                        }
                    },
                    {
                        tag_code: "password",
                        type: "input",
                        attrs: {
                            name: gettext("登陆密码"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "key",
                        type: "input",
                        attrs: {
                            name: gettext("登陆秘钥"),
                            width: '100px',
                            editable: true
                        }
                    }
                ],
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
