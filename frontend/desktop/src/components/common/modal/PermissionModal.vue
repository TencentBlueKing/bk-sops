/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        width="768"
        ext-cls="permission-dialog"
        :mask-close="false"
        :header-position="'left'"
        :title="''"
        :value="isModalShow"
        @cancel="onCloseDialog">
        <div class="permission-content">
            <div class="permission-header">
                <span class="title-icon">
                    <img :src="lock" alt="permission-lock" class="lock-img" />
                </span>
                <h3>{{$t('该操作需要以下权限')}}</h3>
            </div>
            <table class="permission-table table-header">
                <thead>
                    <tr>
                        <th width="20%">{{$t('系统')}}</th>
                        <th width="30%">{{$t('需要申请的资源')}}</th>
                        <th width="50%">{{$t('关联的资源实例')}}</th>
                    </tr>
                </thead>
            </table>
            <div class="table-content">
                <table class="permission-table">
                    <tbody>
                        <tr v-for="(permission, index) in list" :key="index">
                            <td width="20%"></td>
                            <td width="30%">{{permission.action_name}}</td>
                            <td width="50%">{{getResource(permission)}}</td>
                        </tr>
                        <tr v-if="false">
                            <td class="no-data" colspan="2">{{$t('无数据')}}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="permission-footer" slot="footer">
            <div class="button-group">
                <bk-button theme="primary" :loading="loading" @click="goToApply">{{ $t('去申请') }}</bk-button>
                <bk-button theme="default" @click="onCloseDialog">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
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
                lock: require('../../../assets/images/lock-radius.svg')
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
                const type = permission.resource_type_name
                if (permission.resources.length === 0) {
                    return type
                }

                const names = permission.resources.map(res => {
                    return res.map(item => item.resource_name).join(',')
                }).join(',')
                return type + '：' + names
            },
            goToApply () {
                if (this.loading) {
                    return
                }

                if (self === top) {
                    window.open(this.url, '__blank')
                } else {
                    window.PAAS_API.open_other_app('bk_iam_app', this.url)
                }
            },
            onCloseDialog () {
                this.isModalShow = false
            }
        }
    }
</script>
<style lang="scss" scoped>
    /deep/ .permission-content {
        .permission-header {
            text-align: center;
            .title-icon {
                display: inline-block;
            }
            .lock-img {
                width: 120px;
            }
            h3 {
                margin: 6px 0 24px;
                color: #63656e;
                font-size: 20px;
                font-weight: normal;
                line-height: 1;
            }
        }
        .permission-table {
            width: 100%;
            color: #63656e;
            border-bottom: 1px solid #e7e8ed;
            border-collapse: collapse;
            table-layout: fixed;
            th,
            td {
                padding: 12px 18px;
                font-size: 12px;
                text-align: left;
                border-bottom: 1px solid #e7e8ed;
            }
            th {
                color: #313238;
                background: #f5f6fa;
            }
        }
        .table-content {
            max-height: 180px;
            border-bottom: 1px solid #e7e8ed;
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
    .button-group {
        .bk-button {
            margin-left: 7px;
        }
    }
    
</style>
