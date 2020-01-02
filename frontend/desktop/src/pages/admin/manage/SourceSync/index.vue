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
    <div class="source-manage">
        <bk-button
            theme="primary"
            class="sync-btn"
            :loading="pending"
            @click="onTaskSyncClick">
            {{i18n.sync}}
        </bk-button>
        <div class="table-container" v-bkloading="{ isLoading: listLoading, opacity: 1 }">
            <table class="sync-table">
                <thead>
                    <tr>
                        <th width="10%" style="padding: 12px 30px;">ID</th>
                        <th width="25%">{{i18n.startTime}}</th>
                        <th width="25%">{{i18n.endTime}}</th>
                        <th width="10%">{{i18n.operator}}</th>
                        <th width="10%">{{i18n.status}}</th>
                        <th width="10%">{{i18n.triggerType}}</th>
                        <th width="10%">{{i18n.operation}}</th>
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
                                size="mini"
                                class="view-detail"
                                @click="onViewDetailClick(item)">
                                {{i18n.viewDetail}}
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
                    <span> {{i18n.total}} {{totalCount}} {{i18n.item}}{{i18n.comma}} {{i18n.currentPageTip}} {{currentPage}} {{i18n.page}}</span>
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
            :title="i18n.detail"
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
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'SourceManage',
        components: {
            NoData
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
                    sync: gettext('同步到本地缓存'),
                    startTime: gettext('开始时间'),
                    endTime: gettext('结束时间'),
                    operator: gettext('操作人'),
                    status: gettext('状态'),
                    triggerType: gettext('触发方式'),
                    operation: gettext('操作'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    detail: gettext('详细信息'),
                    viewDetail: gettext('查看详情'),
                    manual: gettext('手动'),
                    auto: gettext('自动')
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
                    this.list = syncTaskData.objects
                    this.totalCount = syncTaskData.meta.total_count
                    const totalPage = Math.ceil(this.totalCount / this.countPerPage)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (err) {
                    errorHandler(err, this)
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
                } catch (err) {
                    errorHandler(err, this)
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
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        padding: 20px 60px 60px;
        background: #f4f7fa;
        .sync-btn {
            height: 32px;
            line-height: 32px;
        }
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
                height: 400px;
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
                color: #3c96ff;
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
        /deep/ .bk-dialog-footer {
            display: none;
        }
    }
</style>
