/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="source-manage">
        <bk-button
            v-if="!hasEditPerm"
            v-cursor="{ active: true }"
            theme="primary"
            class="btn-permission-disable"
            @click="applyEditPerm">
            {{$t('同步到本地缓存')}}
        </bk-button>
        <bk-button
            v-else
            theme="primary"
            :loading="pending"
            @click="onTaskSyncClick">
            {{$t('同步到本地缓存')}}
        </bk-button>
        <div class="table-container" v-bkloading="{ isLoading: listLoading, opacity: 1, zIndex: 100 }">
            <table class="sync-table">
                <thead>
                    <tr>
                        <th width="10%" style="padding: 12px 30px;">ID</th>
                        <th width="25%">{{$t('开始时间')}}</th>
                        <th width="25%">{{$t('结束时间')}}</th>
                        <th width="10%">{{$t('操作人')}}</th>
                        <th width="10%">{{$t('状态')}}</th>
                        <th width="10%">{{$t('触发方式')}}</th>
                        <th width="10%">{{$t('操作')}}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in list" :key="item.id">
                        <td style="padding: 12px 30px;">{{item.id}}</td>
                        <td>{{item.start_time || '--'}}</td>
                        <td>{{item.finish_time || '--'}}</td>
                        <td>{{item.creator}}</td>
                        <td>
                            <div class="task-status">
                                <i :class="getStatusCls(item.status)"></i>
                                {{item.status_display}}
                            </div>
                        </td>
                        <td>{{i18n[item.create_method]}}</td>
                        <td>
                            <bk-button
                                theme="default"
                                size="small"
                                class="view-detail"
                                @click="onViewDetailClick(item)">
                                {{$t('查看详情')}}
                            </bk-button>
                        </td>
                    </tr>
                    <tr v-if="list.length === 0">
                        <td colspan="7" class="empty-data">
                            <no-data></no-data>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div class="panagation" v-if="totalPage > 1">
                <div class="page-info">
                    <span> {{$t('共')}} {{totalCount}} {{$t('条记录')}}{{$t('，')}} {{$t('当前第')}} {{currentPage}} {{$t('页')}}</span>
                </div>
                <bk-pagination
                    :current.sync="currentPage"
                    :count="totalCount"
                    :limit="15"
                    @change="onPageChange">
                </bk-pagination>
            </div>
        </div>
        <bk-dialog
            v-if="isDetailDialogShow"
            width="800"
            padding="20px"
            ext-cls="common-dialog"
            header-position="left"
            :title="$t('详细信息')"
            :mask-close="false"
            :value="isDetailDialogShow"
            @cancel="isDetailDialogShow = false">
            <div slot="content" class="detail-content">
                <pre>{{detail}}</pre>
            </div>
            <div slot="footer"></div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'SourceSync',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            hasEditPerm: Boolean,
            editPermLoading: Boolean
        },
        data () {
            return {
                list: [],
                currentPage: 1,
                totalPage: 1,
                countPerPage: 15,
                totalCount: 0,
                listLoading: true,
                pending: false,
                isDetailDialogShow: false,
                detail: '',
                i18n: {
                    manual: i18n.t('手动'),
                    auto: i18n.t('自动')
                }
            }
        },
        created () {
            this.getSyncTask()
        },
        methods: {
            ...mapActions('manage', [
                'loadSyncTask',
                'createSyncTask'
            ]),
            async getSyncTask () {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage
                }
                try {
                    this.listLoading = true

                    const syncTaskData = await this.loadSyncTask(data)
                    this.list = syncTaskData.results
                    this.totalCount = syncTaskData.count
                    const totalPage = Math.ceil(this.totalCount / this.countPerPage)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            async onTaskSyncClick () {
                try {
                    if (this.pending) {
                        return
                    }
                    this.pending = true
                    await this.createSyncTask()
                    this.getSyncTask()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending = false
                }
            },
            getStatusCls (status) {
                let cls = ''
                if (status === 'RUNNING') {
                    cls = 'running common-icon-dark-circle-ellipsis'
                } else if (status === 'FAILED') {
                    cls = 'failed common-icon-dark-circle-close'
                } else {
                    cls = 'finished bk-icon icon-check-circle-shape'
                }
                return cls
            },
            onViewDetailClick (data) {
                this.detail = data.details
                this.isDetailDialogShow = true
            },
            onPageChange (page) {
                this.currentPage = page
                this.getSyncTask()
            },
            applyEditPerm () {
                if (this.editPermLoading) {
                    return
                }
                this.applyForPermission(['admin_edit'])
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        padding: 20px 24px;
        background: #f4f7fa;
        .table-container {
            min-height: 400px;
        }
        .sync-table {
            margin-top: 20px;
            width: 100%;
            border: 1px solid #ddE4eb;
            border-collapse: collapse;
            th,
            td {
                padding: 12px;
                font-size: 12px;
                color: #313238;
                border-top: 1px solid #dde4eb;
                text-align: left;
            }
            th {
                font-weight: 500;
                background: #fafbfd;
            }
            td {
                background: #ffffff;
            }
            .empty-data {
                padding: 0;
            }
            .view-detail {
                padding: 0;
                color: #3a84ff;
                border: none;
                &:active {
                    background: #ffffff;
                }
            }
            .running {
                color: #3a84ff;
            }
            .failed {
                color: #ff5757;
            }
            .finished {
                color: #30d878;
            }
        }
        .panagation {
            padding: 10px 20px;
            text-align: right;
            border: 1px solid #dde4eb;
            border-top: none;
            background: #ffff;
            .page-info {
                float: left;
                line-height: 36px;
                font-size: 12px;
            }
            .bk-page {
                display: inline-block;
            }
        }
        .detail-content {
            padding: 10px;
            height: 320px;
            overflow: auto;
            color: #ffffff;
            background: #313238;
            font-size: 12px;
            pre {
                margin: 0;
                word-break: break-all;
            }
        }
        ::v-deep .bk-dialog-footer {
            display: none;
        }
    }
</style>
