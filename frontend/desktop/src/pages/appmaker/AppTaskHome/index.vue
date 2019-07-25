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
    <div class="appmaker-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.taskRecord"></BaseTitle>
            <div class="operation-area clearfix">
                <div class="appmaker-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput" />
                    <i class="common-icon-search"></i>
                </div>
            </div>
            <div class="appmaker-table-content">
                <table v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <thead>
                        <tr>
                            <th class="appmaker-id">ID</th>
                            <th class="appmaker-name">{{ i18n.name }}</th>
                            <th class="appmaker-time">{{ i18n.startedTime }}</th>
                            <th class="appmaker-time">{{ i18n.finishedTime }}</th>
                            <th class="appmaker-category">{{ i18n.category }}</th>
                            <th class="appmaker-creator">{{ i18n.creator }}</th>
                            <th class="appmaker-operator">{{ i18n.operator }}</th>
                            <th class="appmaker-status">{{ i18n.status }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, index) in appmakerList" :key="item.id">
                            <td class="appmaker-id">{{item.id}}</td>
                            <td class="appmaker-name">
                                <router-link
                                    :to="`/appmaker/${item.create_info}/execute/${item.business.cc_id}/?instance_id=${item.id}`">
                                    {{item.name}}
                                </router-link>
                            </td>
                            <td class="appmaker-time">{{item.start_time || '--'}}</td>
                            <td class="appmaker-time">{{item.finish_time || '--'}}</td>
                            <td class="appmaker-category">{{item.category_name}}</td>
                            <td class="appmaker-creator">{{item.creator_name}}</td>
                            <td class="appmaker-operator">{{item.executor_name || '--'}}</td>
                            <td class="appmaker-status">
                                <span :class="executeStatus[index] ? executeStatus[index].cls : ''"></span>
                                <span v-if="executeStatus[index]">{{executeStatus[index].text}}</span>
                            </td>
                        </tr>
                        <tr v-if="!appmakerList || !appmakerList.length" class="empty-tr">
                            <td colspan="8">
                                <div class="empty-data"><NoData /></div>
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
                        :limit="countPerPage"
                        :limit-list="[15,20,30]"
                        :show-limit="false"
                        @change="onPageChange">
                    </bk-pagination>
                </div>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import toolsUtils from '@/utils/tools.js'
    export default {
        name: 'appmakerTaskHome',
        components: {
            CopyrightFooter,
            BaseTitle,
            NoData
        },
        props: ['cc_id', 'app_id'],
        data () {
            return {
                i18n: {
                    placeholder: gettext('请输入ID或流程名称'),
                    startedTime: gettext('执行开始'),
                    finishedTime: gettext('执行结束'),
                    name: gettext('任务名称'),
                    category: gettext('任务类型'),
                    creator: gettext('创建人'),
                    operator: gettext('执行人'),
                    status: gettext('状态'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    taskRecord: gettext('任务记录')
                },
                listLoading: true,
                currentPage: 1,
                totalPage: 1,
                countPerPage: 15,
                totalCount: 0,
                isDeleteDialogShow: false,
                theDeleteTemplateId: undefined,
                pending: {
                    delete: false,
                    authority: false
                },
                searchStr: '',
                appmakerList: [],
                executeStatus: [] // 任务执行状态
            }
        },
        computed: {
        },
        created () {
            this.getAppmakerList()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('taskList/', [
                'loadTaskList'
            ]),
            ...mapActions('task/', [
                'getInstanceStatus'
            ]),
            async getAppmakerList () {
                this.listLoading = true
                try {
                    const data = {
                        limit: this.countPerPage,
                        offset: (this.currentPage - 1) * this.countPerPage,
                        create_method: 'app_maker',
                        create_info: this.app_id,
                        q: this.searchStr
                    }
                    const appmakerListData = await this.loadTaskList(data)
                    const list = appmakerListData.objects
                    this.appmakerList = list
                    this.totalCount = appmakerListData.meta.total_count
                    const totalPage = Math.ceil(this.totalCount / this.countPerPage)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                    this.executeStatus = list.map((item, index) => {
                        const status = {}
                        if (item.is_finished) {
                            status.cls = 'finished bk-icon icon-check-circle-shape'
                            status.text = gettext('完成')
                        } else if (item.is_started) {
                            status.cls = 'loading common-icon-loading'
                            this.getExecuteDetail(item, index)
                        } else {
                            status.cls = 'created common-icon-dark-circle-shape'
                            status.text = gettext('未执行')
                        }
                        return status
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.listLoading = false
                }
            },
            async getExecuteDetail (task, index) {
                const data = {
                    instance_id: task.id,
                    cc_id: task.business.cc_id
                }
                try {
                    const detailInfo = await this.getInstanceStatus(data)
                    if (detailInfo.result) {
                        const state = detailInfo.data.state
                        const status = {}
                        switch (state) {
                            case 'RUNNING':
                            case 'BLOCKED':
                                status.cls = 'running common-icon-dark-circle-ellipsis'
                                status.text = gettext('执行中')
                                break
                            case 'SUSPENDED':
                                status.cls = 'execute common-icon-dark-circle-pause'
                                status.text = gettext('暂停')
                                break
                            case 'NODE_SUSPENDED':
                                status.cls = 'execute'
                                status.text = gettext('节点暂停')
                                break
                            case 'FAILED':
                                status.cls = 'failed common-icon-dark-circle-close'
                                status.text = gettext('失败')
                                break
                            case 'REVOKED':
                                status.cls = 'revoke common-icon-dark-circle-shape'
                                status.text = gettext('撤销')
                                break
                            default:
                                status.text = gettext('未知')
                        }
                        this.executeStatus.splice(index, 1, status)
                    } else {
                        errorHandler(detailInfo, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onPageChange (page) {
                this.currentPage = page
                this.getAppmakerList()
            },
            searchInputhandler () {
                this.currentPage = 1
                this.getAppmakerList()
            },
            statusMethod (is_started, is_finished) {
                let status = ''
                if (is_finished) {
                    status = gettext('完成')
                } else if (is_started) {
                    status = gettext('执行中')
                } else {
                    status = gettext('未执行')
                }
                return status
            },
            statusClass (is_started, is_finished) {
                let statusClass = ''
                if (is_finished) {
                    statusClass = { success: true }
                } else if (is_started) {
                    statusClass = { warning: true }
                } else {
                    statusClass = { primary: true }
                }
                return statusClass
            }

        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.appmaker-container {
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: #fafafa;
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
}
.operation-area {
    margin: 20px 0;
    .appmaker-search {
        float: right;
        position: relative;
    }
    .search-input {
        padding: 0 40px 0 10px;
        width: 360px;
        height: 32px;
        line-height: 32px;
        font-size: 14px;
        background: $whiteDefault;
        border: 1px solid $commonBorderColor;
        border-radius: 4px;
        outline: none;
        &:hover {
            border-color: #c0c4cc;
        }
        &:focus {
            border-color: $blueDefault;
            & + i {
                color: $blueDefault;
            }
        }
    }
    .common-icon-search {
        position: absolute;
        right: 15px;
        top: 8px;
        color: $commonBorderColor;
    }
}
.appmaker-table-content {
    table {
        width: 100%;
        border: 1px solid #ebebeb;
        border-collapse: collapse;
        font-size: 12px;
        background: $whiteDefault;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: $whiteNodeBg;
        }
        th,td {
            padding: 11px;
            text-align: left;
            border-bottom: 1px solid $commonBorderColor;
        }
        td {
            color: #63656e
        }
        th {
            background: #fafafa;
        }
        .appmaker-id {
            padding-left: 20px;
            width: 80px;
        }
        .appmaker-name {
            text-align: left;
            a {
                display: block;
                width: 100%;
                color: #3c96ff;
                text-overflow: ellipsis;
                white-space: nowrap;
                word-break: break-all;
                overflow: hidden;
            }
        }
        .appmaker-type {
            width: 110px;
        }
        .appmaker-time {
            width: 220px;
        }
        .appmaker-creator {
            width: 110px;
        }
        .appmaker-operator {
            width: 110px;
        }
        .appmaker-category {
            width: 110px;
        }
        .appmaker-name {
            width: 220px;
        }
        .appmaker-status {
            width: 84px;
            .common-icon-dark-circle-shape {
                display: inline-block;
                transform: scale(0.9);
                font-size: 12px;
                color: #979BA5;
            }
             .common-icon-dark-circle-ellipsis {
                color: #3c96ff;
                font-size: 12px;
            }
            .icon-check-circle-shape {
                color: $greenDefault;
            }
            .common-icon-dark-circle-close {
                color: $redDefault;
            }
            &.revoke {
                color: $blueDisable;
            }
            .common-icon-loading {
                display: inline-block;
                animation: bk-button-loading 1.4s infinite linear;
            }
            @keyframes bk-button-loading {
                from {
                    -webkit-transform: rotate(0);
                    transform: rotate(0); }
                to {
                    -webkit-transform: rotate(360deg);
                    transform: rotate(360deg);
                }
            }
        }
    }
    .btn-size-mini {
        height: 24px;
        line-height: 22px;
        padding: 0 11px;
        font-size: 12px;
    }
    .empty-data {
        padding: 120px 0;
    }
}
.panagation {
    padding: 10px 20px;
    text-align: right;
    border: 1px solid #dde4eb;
    border-top: none;
    background: #fafbfd;
    .page-info {
        float: left;
        line-height: 36px;
        font-size: 14px;
    }
    .bk-page {
        display: inline-block;
    }
}
.success {
    color:#30d878;
}
.warning {
    color: #f8b53f;
}
.primary {
    color: #4a9bff;
}
</style>
