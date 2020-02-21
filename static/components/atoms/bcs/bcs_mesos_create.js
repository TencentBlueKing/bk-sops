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
    $.atoms.bcs_mesos_create = [
        {
            "tag_code": "bcs_create_data",
            "type": "combine",
            attrs: {
                "name": gettext("Create配置"),
                hookable: true,
                children: [
                    {
                        "type": "input",
                        "attrs": {
                            "name": gettext("BCS项目ID"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                        },
                        "events": [],
                        "methods": {
                            _tag_init: function () {
                                this.emit_event(this.tagCode, "change", this.value)
                            }
                        },
                        "tag_code": "bcs_create_project_id"
                    },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("对象类型"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                                {
                                    "text": "Deployment",
                                    "value": "Deployment"
                                },
                                {
                                    "text": "Application",
                                    "value": "Application"
                                }
                            ],
                            "remote": false,
                            "remote_url": "",
                            "remote_data_init": function (e) { return e },
                            "placeholder": gettext("请选择对象类型"),
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_create_obj_type"
                    },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("集群"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                            ],
                            "remote": true,
                            "remote_url": function () {
                                var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                if (!project_id || project_id.length != 32) {
                                    return ''
                                }
                                return this.clusters_url(project_id)
                            },
                            "remote_data_init": function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data
                            },
                            "placeholder": gettext("请选择集群"),
                        },
                        "events": [
                            {
                                source: "bcs_create_project_id",
                                type: "change",
                                action: function (value) {
                                    if (!value || value.length != 32) {
                                        return
                                    }
                                    this.remote_url = this.clusters_url(value)
                                    this.remoteMethod()
                                }
                            }
                        ],
                        "methods": {
                            clusters_url: function (project_id) {
                                url = $.context.get('site_url') + 'pipeline/bcs_get_clusters/'
                                url += '?project_id=' + project_id
                                return url
                            }
                        },
                        "tag_code": "bcs_create_set"
                    },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("模板集"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                            ],
                            "remote": true,
                            "remote_url": function () {
                                var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                if (!project_id || project_id.length != 32) {
                                    return ''
                                }
                                return this.musters_url($.context.getBkBizId(), value)
                            },
                            "remote_data_init": function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data
                            },
                            "placeholder": gettext("请选择模板集"),
                        },
                        "events": [
                            {
                                source: "bcs_create_project_id",
                                type: "change",
                                action: function (value) {
                                    if (!value || value.length != 32) {
                                        return
                                    }
                                    this.remote_url = this.musters_url($.context.getBkBizId(), value)
                                    this.remoteMethod()
                                }
                            }
                        ],
                        "methods": {
                            _tag_init: function () {
                                this.emit_event(this.tagCode, "change", this.value)
                            },
                            musters_url: function (bk_biz_id, project_id) {
                                url = $.context.get('site_url') + 'pipeline/bcs_get_musters/'
                                url += '?project_id=' + project_id + '&bk_biz_id=' + bk_biz_id
                                return url
                            }
                        },
                        "tag_code": "bcs_create_muster"
                    },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("模板集版本"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                            ],
                            "remote": true,
                            "remote_url": function () {
                                var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                if (!project_id || project_id.length != 32) {
                                    return ''
                                }
                                var muster_id = this.get_parent().get_child('bcs_create_muster').value
                                if (!muster_id) {
                                    return ''
                                }
                                return this.muster_versions_url($.context.getBkBizId(), project_id, muster_id)
                            },
                            "remote_data_init": function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data
                            },
                            "placeholder": gettext("请选择模板集版本"),
                        },
                        "events": [
                            {
                                source: "bcs_create_muster",
                                type: "change",
                                action: function (value) {
                                    var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                    if (!project_id || project_id.length != 32) {
                                        return ''
                                    }
                                    this.remote_url = this.muster_versions_url($.context.getBkBizId(), project_id, value)
                                    this.remoteMethod()
                                }
                            }
                        ],
                        "methods": {
                            _tag_init: function () {
                                this.emit_event(this.tagCode, "change", this.value)
                            },
                            muster_versions_url: function (bk_biz_id, project_id, muster_id) {
                                url = $.context.get('site_url') + 'pipeline/bcs_get_muster_versions/'
                                url += '?project_id=' + project_id + '&bk_biz_id=' + bk_biz_id + '&muster_id=' + muster_id
                                return url
                            }
                        },
                        "tag_code": "bcs_create_muster_ver"
                    },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("资源"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                            ],
                            "remote": true,
                            "multiple": true,
                            "remote_url": function () {
                                var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                if (!project_id || project_id.length != 32) {
                                    return ''
                                }
                                var version_id = this.get_parent().get_child('bcs_create_muster_ver').value
                                if (!version_id) {
                                    return ''
                                }
                                var obj_type = this.get_parent().get_child('bcs_create_obj_type').value
                                return this.version_templates_url($.context.getBkBizId(), project_id, version_id, obj_type)
                            },
                            "remote_data_init": function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data
                            },
                            "placeholder": gettext("请选择资源"),
                        },
                        "events": [
                            {
                                source: "bcs_create_muster_ver",
                                type: "change",
                                action: function (value) {
                                    if (!value) {
                                        return
                                    }
                                    var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                    if (!project_id || project_id.length != 32) {
                                        return ''
                                    }
                                    var obj_type = this.get_parent().get_child('bcs_create_obj_type').value
                                    this.remote_url = this.version_templates_url($.context.getBkBizId(), project_id, value, obj_type)
                                    this.remoteMethod()
                                }
                            },
                            {
                                source: "bcs_create_obj_type",
                                type: "change",
                                action: function (value) {
                                    var project_id = this.get_parent().get_child('bcs_create_project_id').value
                                    if (!project_id || project_id.length != 32) {
                                        return ''
                                    }
                                    var version_id = this.get_parent().get_child('bcs_create_muster_ver').value
                                    if (!version_id) {
                                        return ''
                                    }
                                    this.remote_url = this.version_templates_url($.context.getBkBizId(), project_id, version_id, value)
                                    this.remoteMethod()
                                }
                            }
                        ],
                        "methods": {
                            version_templates_url: function (bk_biz_id, project_id, version_id, obj_type) {
                                url = $.context.get('site_url') + 'pipeline/bcs_get_version_templates/'
                                url += '?project_id=' + project_id + '&bk_biz_id=' + bk_biz_id + '&version_id=' + version_id + '&obj_type=' + obj_type
                                return url
                            }
                        },
                        "tag_code": "bcs_create_template"
                    },
                    {
                        "type": "datatable",
                        "attrs": {
                            "name": gettext("命名空间参数"),
                            "hookable": false,
                            "default": "",
                            "columns": [
                                {
                                    "tag_code": "namespace_name",
                                    "type": "input",
                                    "attrs": {
                                        "name": "namespace名称"
                                    }
                                },
                                {
                                    "tag_code": "key",
                                    "type": "input",
                                    "attrs": {
                                        "name": "Key"
                                    }
                                },
                                {
                                    "tag_code": "value",
                                    "type": "input",
                                    "attrs": {
                                        "name": "Value"
                                    }
                                }
                            ],
                            "editable": true,
                            "value": [],
                            "add_btn": true,
                            "empty_text": "无数据",
                            "remote_url": "",
                            "remote_data_init": function (e) { return e },
                            "table_buttons": []
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_create_vars"
                    }
                ]
            },
            "events": [],
        }
    ]
})();