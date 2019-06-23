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
<template>
    <bk-dialog
        ext-cls="permission-dialog"
        :is-show="isModalShow"
        :title="' '"
        :width="'600'"
        padding="0 24px 40px 24px"
        :has-header="true"
        :has-footer="true"
        :quick-close="false"
        :close-icon="true"
        @cancel="onCloseDialog">
        <div class="permission-content" slot="content">
            <div class="permission-header">
                <span class="title-icon"><i class="icon common-icon-lock-closed"></i></span>
                <h3>{{i18n.permissionTitle}}</h3>
            </div>
            <table class="permission-table table-header">
                <thead>
                    <tr>
                        <th width="60%">{{i18n.resource}}</th>
                        <th width="40%">{{i18n.requiredPermissions}}</th>
                    </tr>
                </thead>
            </table>
            <div class="table-content">
                <table class="permission-table">
                    <tbody>
                        <tr v-for="(permission, index) in list" :key="index">
                            <td width="60%">{{getResource(permission)}}</td>
                            <td width="40%">{{permission.action_name}}</td>
                        </tr>
                        <tr v-if="false">
                            <td class="no-data" colspan="3">{{i18n.noData}}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="permission-footer" slot="footer">
            <bk-button type="primary" :loading="loading" @click="goToApply">{{ i18n.apply }}</bk-button>
            <bk-button type="default" @click="onCloseDialog">{{ i18n.cancel }}</bk-button>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'permissionModal',
        props: {},
        data () {
            return {
                isModalShow: false,
                list: [],
                loading: false,
                i18n: {
                    permissionTitle: gettext('没有权限访问或操作此资源'),
                    system: gettext('系统'),
                    resource: gettext('资源'),
                    requiredPermissions: gettext('需要申请的权限'),
                    noData: gettext('无数据'),
                    apply: gettext('去申请'),
                    cancel: gettext('取消')
                }
            }
        },
        watch: {
            isModalShow (val) {
                if (val) {
                    this.loadPermissionUrl()
                }
            }
        },
        methods: {
            ...mapActions([
                'getPermissionUrl'
            ]),
            async loadPermissionUrl () {
                try {
                    this.loading = true
                    const permission = this.list
                    const res = await this.getPermissionUrl(JSON.stringify(permission))
                    this.url = res.data.url
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.loading = false
                }
            },
            show (data) {
                this.isModalShow = true
                this.list = data
            },
            getResource (permission) {
                return permission.resources.map(res => {
                    return res.map(item => item.resource_name).join(',')
                }).join(',')
            },
            goToApply () {
                if (this.loading) {
                    return
                }
                window.open(this.url, '__blank')
            },
            onCloseDialog () {
                this.isModalShow = false
            }
        }
    }
</script>
<style lang="scss" scoped>
    .permission-dialog {
        z-index: 1501;
    }
    /deep/ .permission-content {
        margin-top: -26px;
        .permission-header {
            text-align: center;
            .icon {
                font-size: 60px;
                color: #cfd1d6;
            }
            h3 {
                margin: 10px 0 30px;
                color: #979ba5;
                font-size: 24px;
            }
        }
        .permission-table {
            width: 100%;
            color: #63656e;
            border: 1px solid #dcdee5;
            border-collapse: collapse;
            table-layout: fixed;
            th,
            td {
                padding: 12px 18px;
                font-size: 12px;
                text-align: left;
                border-bottom: 1px solid #dcdee5;
                border-right: 1px solid #dcdee5;
            }
            th {
                color: #313238;
                background: rgb(250, 251, 253);
            }
        }
        .table-content {
            max-height: 180px;
            border-bottom: 1px solid #dcdee5;
            border-top: none;
            overflow: auto;
            .permission-table {
                border-top: none;
                border-bottom: none;
                td:last-child {
                    border-right: none;
                }
                tr:last-child td {
                    border-bottom: none;
                }
            }
            .no-data {
                text-align: center;
                color: #999999;
            }
        }
    }
    /deep/ .bk-dialog-footer.bk-d-footer {
        height: 50px;
        line-height: 50px;
        .permission-footer {
            padding: 0 24px;
            text-align: right;
        }
        .bk-button {
            height: 32px;
            line-height: 30px;
        }
    }
    
</style>
