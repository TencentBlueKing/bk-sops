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
        :z-index="2010"
        :mask-close="false"
        :header-position="'left'"
        :title="''"
        :value="isModalShow"
        @cancel="onCloseDialog">
        <div class="permission-modal">
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
                        <th width="30%">{{$t('需要申请的权限')}}</th>
                        <th width="50%">{{$t('关联的资源实例')}}</th>
                    </tr>
                </thead>
            </table>
            <div class="table-content">
                <table class="permission-table">
                    <tbody>
                        <template v-if="permissionData.actions && permissionData.actions.length > 0">
                            <tr v-for="(action, index) in permissionData.actions" :key="index">
                                <td width="20%">{{permissionData.system_name}}</td>
                                <td width="30%">{{action.name}}</td>
                                <td width="50%">
                                    <p
                                        class="resource-type-item"
                                        v-for="(reItem, reIndex) in getResource(action.related_resource_types)"
                                        :key="reIndex">
                                        {{reItem}}
                                    </p>
                                </td>
                            </tr>
                        </template>
                        <tr v-else>
                            <td class="no-data" colspan="3">{{$t('无数据')}}</td>
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
    import openOtherApp from '@/utils/openOtherApp.js'

    export default {
        name: 'permissionModal',
        props: {},
        data () {
            return {
                isModalShow: false,
                permissionData: {},
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
                'getIamUrl'
            ]),
            async loadPermissionUrl () {
                try {
                    this.loading = true
                    const res = await this.getIamUrl(this.permissionData)
                    if (res.result) {
                        this.url = res.data.url
                    } else {
                        errorHandler(res, this)
                    }
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.loading = false
                }
            },
            show (data) {
                this.isModalShow = true
                this.permissionData = data
            },
            getResource (resources) {
                if (resources.length === 0) {
                    return ['--']
                }

                const data = []
                resources.forEach(resource => {
                    if (resource.instances.length > 0) {
                        resource.instances.forEach(instanceItem => {
                            instanceItem.forEach(item => {
                                data.push(`${item.type_name}：${item.name}`)
                            })
                        })
                    }
                })
                return data
            },
            goToApply () {
                if (this.loading) {
                    return
                }

                openOtherApp(window.BK_IAM_APP_CODE, this.url)
            },
            onCloseDialog () {
                this.isModalShow = false
            }
        }
    }
</script>
<style lang="scss" scoped>
    .permission-modal {
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
                word-break: break-all;
            }
            th {
                color: #313238;
                background: #f5f6fa;
            }
        }
        .table-content {
            max-height: 260px;
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
                .resource-type-item {
                    padding: 0;
                    margin: 0;
                }
            }
            .no-data {
                padding: 30px;
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
