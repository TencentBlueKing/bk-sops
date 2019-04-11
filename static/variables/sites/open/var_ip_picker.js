/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
(function () {
    function cc_format_ip_topo_data(module_hosts, cc_topo) {
        var tree_data = [];
        $.each(cc_topo, function (index, item) {
            var tree_item = {
                'id': item['id'],
                'label': item['label']
            };
            if (item['id'] in module_hosts) {
                tree_item['children'] = module_hosts[item['id']]
            } else if ('children' in item) {
                tree_item['children'] = cc_format_ip_topo_data(module_hosts, item['children']);
            }
            tree_data.push(tree_item)
        });
        return tree_data
    }

    $.atoms.var_ip_picker = [
        {
            tag_code: "ip_picker",
            type: "combine",
            attrs: {
                name: "IP/DNS选择器",
                hookable: true,
                children: [
                    {
                        tag_code: "var_ip_method",
                        type: "select",
                        attrs: {
                            name: gettext("填参方式"),
                            items: [
                                {value: "custom", text: gettext("自定义输入")},
                                {value: "tree", text: gettext("通过配置平台拓扑获取")},
                            ],
                            default: "custom",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function () {
                                    var self = this;

                                    function init_self(self) {
                                        setTimeout(function () {
                                            self.emit_event(self.tag_code, "change", self.value)
                                        }, 500)
                                    }

                                    init_self(self);
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_custom_value",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行符分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的")
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'custom') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'custom') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_tree",
                        type: "tree",
                        attrs: {
                            name: gettext("拓扑树"),
                            hidden: true,
                            remote: false,
                            default_expand_all: false,
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'tree') {
                                        self.show();

                                        function init_self(self) {
                                            setTimeout(function () {
                                                self.emit_event('var_ip_method', "change", value)
                                            }, 500)
                                        }

                                        init_self(self);
                                    } else {
                                        self.hide();
                                    }
                                }
                            },
                            {
                                source: "var_ip_tree",
                                type: "init",
                                action: function () {
                                    var self = this;

                                    function init_self(self) {
                                        setTimeout(function () {
                                            self.emit_event(self.tag_code, "change", self.value)
                                        }, 500)
                                    }

                                    init_self(self);
                                }
                            },
                            {
                                source: "var_ip_tree",
                                type: "change",
                                action: function () {
                                    var self = this;
                                    var select_module_list = [];
                                    $.each(self.value, function (index, value) {
                                        if (value.split('_')[0] === 'module') {
                                            select_module_list.push(value.split('_')[1])
                                        }
                                    });
                                    if (select_module_list.length > 0) {
                                        $.ajax({
                                            url: $.context.site_url + 'pipeline/cc_get_host_by_module_id/' + $.context.biz_cc_id + '/',
                                            type: 'GET',
                                            traditional: true,
                                            data: {
                                                query: select_module_list
                                            },
                                            dataType: 'json',
                                            success: function (resp) {
                                                if (resp.result) {
                                                    self.items = cc_format_ip_topo_data(resp.data, self.items);
                                                }
                                            },
                                            error: function (resp) {
                                                show_msg(gettext("请求后台接口异常:") + resp.status + ',' + resp.statusText, 'error');
                                            }
                                        })
                                    }
                                }
                            },
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'tree') {
                                        self.show();
                                        $.ajax({
                                            url: $.context.site_url + 'pipeline/cc_search_topo/module/picker/' + $.context.biz_cc_id + '/',
                                            type: 'GET',
                                            dataType: 'json',
                                            success: function (resp) {
                                                if (!resp.result) {
                                                    show_msg(resp.message, 'error');
                                                } else {
                                                    self.items = resp.data;

                                                    if (self.value.length > 0) {
                                                        select_module_list = [];
                                                        $.each(self.value, function (index, value) {
                                                            if (value.split('_')[0] === 'module') {
                                                                if (!(value.split('_')[1] in select_module_list)) {
                                                                    select_module_list.push(value.split('_')[1])
                                                                }
                                                            } else {
                                                                if (!(value.split('_')[0] in select_module_list)) {
                                                                    select_module_list.push(value.split('_')[0])
                                                                }
                                                            }
                                                        });

                                                        $.ajax({
                                                            url: $.context.site_url + 'pipeline/cc_get_host_by_module_id/' + $.context.biz_cc_id + '/',
                                                            type: 'GET',
                                                            traditional: true,
                                                            data: {
                                                                query: select_module_list
                                                            },
                                                            dataType: 'json',
                                                            success: function (resp) {
                                                                if (resp.result) {
                                                                    self.items = cc_format_ip_topo_data(resp.data, self.items);
                                                                }
                                                            },
                                                            error: function (resp) {
                                                                show_msg(gettext("请求后台接口异常:") + resp.status + ',' + resp.statusText, 'error');
                                                            }
                                                        })
                                                    }
                                                }
                                            },
                                            error: function (resp) {
                                                show_msg(gettext("请求后台接口异常:") + resp.status + ',' + resp.statusText, 'error');
                                            }
                                        })
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                ],
            }
        },
    ]
})();
