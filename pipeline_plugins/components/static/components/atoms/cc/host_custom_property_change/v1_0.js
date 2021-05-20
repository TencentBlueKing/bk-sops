(function () {
    $.atoms.cc_host_custom_property_change = [
        {
            tag_code: "cc_ip_list",
            type: "textarea",
            attrs: {
                name: "IP",
                hookable: true,
                placeholder: "输入IP, 多个用英文逗号 `,` 或换行分隔",
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "cc_custom_property",
            type: "select",
            attrs: {
                name: "自定义属性",
                hookable: true,
                placeholder: "请选择主机自定义属性",
                remote_url: $.context.get('site_url') + 'pipeline/cc_search_object_attribute/host/' + $.context.getBkBizId() + '/',
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
            tag_code: "cc_hostname_rule",
            type: "datatable",
            attrs: {
                pagination: true,
                name: "规则定义(主机属性)",
                add_btn: true,
                empty_text: gettext("没有数据"),
                columns: [
                    {
                        tag_code: "field_rule_code",
                        type: "select",
                        attrs: {
                            name: gettext("字段组件"),
                            placeholder: "请选择字段组件",
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                            items: [
                                {text: "主机属性", value: "1"},
                                {text: "set属性", value: "2"},
                                {text: "模块属性", value: "3"},
                            ]
                        }
                    },
                    {
                        tag_code: "field_content",
                        type: "select",
                        attrs: {
                            placeholder: "请选择具体内容",
                            remote_url: '',
                            remote_data_init: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data;
                            },
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                            name: gettext("具体内容"),
                        },
                        events: [
                            {
                                source: "field_rule_code",
                                type: "init",
                                action: function (value) {
                                    if (value !== '') {
                                        var obj_dic = {"1":"host", "2":"set", "3":"module"};
                                        var obj_name = obj_dic[value];
                                        this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_object_attribute_all/' + obj_name+ '/' + $.context.getBkBizId() + '/';
                                        this.remoteMethod();
                                    }
                                }
                            },
                            {
                                source: "field_rule_code",
                                type: "change",
                                action: function (value) {
                                    this.items = [];
                                    if (value !== '') {
                                        var obj_dic = {"1":"host", "2":"set", "3":"module"};
                                        var obj_name = obj_dic[value];
                                        this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_object_attribute_all/' + obj_name+ '/' + $.context.getBkBizId() + '/';
                                        this.remoteMethod();
                                    }
                                }
                            }
                        ],
                    },
                    {
                        tag_code: "field_order",
                        type: "int",
                        attrs: {
                            placeholder: "请填写大于等于1的整数",
                            editable: true,
                            default: 1,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        if (value <= 0 || isNaN(value)) {
                                            result.result = false;
                                            result.error_message = gettext("必须为大于等于1的整数");
                                        }
                                        return result;
                                    }
                                },
                            ],
                            name: gettext("次序"),
                        }
                    }
                ]
            },
        },
        {
            tag_code: "cc_custom_rule",
            type: "datatable",
            attrs: {
                pagination: true,
                name: "规则定义(自定义属性)",
                add_btn: true,
                empty_text: gettext("没有数据"),
                columns: [
                    {
                        tag_code: "field_rule_code",
                        type: "select",
                        attrs: {
                            placeholder: "请选择字段组件",
                            name: gettext("字段组件"),
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                            items: [
                                {text: "ip(.需替换成)", value: "4"},
                                {text: "自增变量", value: "5"},
                                {text: "自定义字符(串)", value: "6"},
                            ]
                        },
                    },
                    {
                        tag_code: "field_content",
                        type: "input",
                        attrs: {
                            placeholder: "请填写具体内容",
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                            name: gettext("具体内容"),
                        }
                    },
                    {
                        tag_code: "field_order",
                        type: "int",
                        attrs: {
                            placeholder: "请填写大于等于1的整数",
                            editable: true,
                            default: 1,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        if (value <= 0 || isNaN(value)) {
                                            result.result = false;
                                            result.error_message = gettext("必须为大于等于1的整数");
                                        }
                                        return result;
                                    }
                                },
                                {
                                    type: "required"
                                }
                            ],
                            name: gettext("次序"),
                        }
                    }
                ]
            },
        },
    ]
})();
