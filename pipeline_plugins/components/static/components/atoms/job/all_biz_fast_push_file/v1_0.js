/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
(function () {
    $.atoms.all_biz_job_fast_push_file = [
        {
            tag_code: "all_biz_cc_id",
            type: "input",
            attrs: {
                name: gettext("全业务ID"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "job_source_files",
            type: "datatable",
            attrs: {
                name: gettext("源文件"),
                editable: true,
                table_buttons: [
                    {
                        type: "export",
                        text: gettext("导出"),
                        callback: function () {
                            this.export2Excel()
                        }
                    },
                    {
                        type: "import",
                        text: gettext("导入")
                    }
                ],
                columns: [
                    {
                        tag_code: "bk_cloud_id",
                        type: "input",
                        attrs: {
                            name: gettext("云区域ID"),
                            placeholder: gettext("默认为0"),
                            width: '90px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "ip",
                        type: "input",
                        attrs: {
                            name: gettext("IP"),
                            width: '150px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "files",
                        type: "textarea",
                        attrs: {
                            name: gettext("文件路径"),
                            placeholder: gettext("多个用换行分隔"),
                            width: '170px',
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
                            name: gettext("执行账户"),
                            width: '80px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
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
        },
        {
            tag_code: "upload_speed_limit",
            type: "input",
            attrs: {
                name: gettext("上传限速"),
                placeholder: gettext("MB/s 若不限速则不填写"),
                hookable: true,
            }
        },
        {
            tag_code: "download_speed_limit",
            type: "input",
            attrs: {
                name: gettext("下载限速"),
                placeholder: gettext("MB/s 若不限速则不填写"),
                hookable: true,
            }
        },
        {
            tag_code: "job_dispatch_attr",
            type: "datatable",
            attrs: {
                name: gettext("分发配置"),
                table_buttons: [
                    {
                        type: "export",
                        text: gettext("导出"),
                        callback: function () {
                            this.export2Excel()
                        }
                    },
                    {
                        type: "import",
                        text: gettext("导入")
                    }
                ],
                hookable: true,
                columns: [
                    {
                        tag_code: "bk_cloud_id",
                        type: "input",
                        attrs: {
                            name: gettext("云区域ID"),
                            placeholder: gettext("默认为0"),
                            width: '90px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },


                    {
                        tag_code: "job_ip_list",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("多IP请使用;分隔"),
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
                            placeholder: gettext("请输入绝对路径（可用[FILESRCIP]代替源IP）"),
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
                            name: gettext("执行账户"),
                            placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                ],
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [],
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
            tag_code: "job_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒，为空时使用JOB默认值"),
                hookable: true,
            }
        }
    ]
})();
