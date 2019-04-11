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
    <div class="audit-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.auditList"></BaseTitle>
            <div class="operation-area">
                <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput" />
            </div>
            <div class="audit-table-content">
                <table v-bkloading="{isLoading: listLoading, opacity: 1}">
                    <thead>
                        <tr>
                            <th class="audit-id">ID</th>
                            <th class="audit-business">{{ i18n.business }}</th>
                            <th class="audit-name">{{ i18n.name }}</th>
                            <th class="audit-time">{{ i18n.startedTime }}</th>
                            <th class="audit-time">{{ i18n.finishedTime }}</th>
                            <th class="audit-category">{{ i18n.category }}</th>
                            <th class="audit-creator">{{ i18n.creator }}</th>
                            <th class="audit-executor">{{ i18n.operator }}</th>
                            <th class="audit-status">{{ i18n.status }}</th>
                            <th class="audit-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, index) in auditList" :key="item.id">
                            <td class="audit-id">{{item.id}}</td>
                            <td class="audit-business">{{item.business.cc_name}}</td>
                            <td class="audit-name">
                                <router-link
                                    :title="item.name"
                                    :to="`/taskflow/execute/${item.business.cc_id}/?instance_id=${item.id}`">
                                    {{item.name}}
                                </router-link>
                            </td>
                            <td class="audit-time">{{item.start_time || '--'}}</td>
                            <td class="audit-time">{{item.finish_time || '--'}}</td>
                            <td class="audit-category">{{item.category_name}}</td>
                            <td class="audit-creator">{{item.creator_name}}</td>
                            <td class="audit-executor">{{item.executor_name || '--'}}</td>
                            <td class="audit-status">
                                <span :class="executeStatus[index] && executeStatus[index].cls"></span>
                                <span v-if="executeStatus[index]">{{executeStatus[index].text}}</span>
                            </td>
                            <td class="audit-operation">
                                <router-link
                                    class="audit-operation-btn"
                                    :to="`/taskflow/execute/${item.business.cc_id}/?instance_id=${item.id}`">
                                    {{ i18n.view }}
                                </router-link>
                            </td>
                        </tr>
                        <tr v-if="!auditList || !auditList.length" class="empty-tr">
                            <td colspan="10">
                                <div class="empty-data"><NoData/></div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div class="panagation" v-if="totalPage > 1">
                    <div class="page-info">
                        <span> {{i18n.total}} {{totalCount}} {{i18n.item}}{{i18n.comma}} {{i18n.currentPageTip}} {{currentPage}} {{i18n.page}}</span>
                    </div>
                    <bk-paging
                        :cur-page.sync="currentPage"
                        :total-page="totalPage"
                        @page-change="onPageChange">
                    </bk-paging>
                </div>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
import NoData from '@/components/common/base/NoData.vue'
import BaseTitle from '@/components/common/base/BaseTitle.vue'
import BaseSearch from '@/components/common/base/BaseSearch.vue'
import toolsUtils from '@/utils/tools.js'
export default {
    name: 'auditTaskHome',
    components: {
        CopyrightFooter,
        BaseTitle,
        BaseSearch,
        NoData
    },
    data () {
        return {
            i18n: {
                auditList: gettext('审计中心'),
                placeholder: gettext('请输入ID或流程名称'),
                business: gettext('所属业务'),
                startedTime: gettext('执行开始'),
                finishedTime: gettext('执行结束'),
                name: gettext('任务名称'),
                category: gettext('任务类型'),
                creator: gettext('创建人'),
                operator: gettext('执行人'),
                status: gettext('状态'),
                operation: gettext('操作'),
                view: gettext('查看'),
                total: gettext('共'),
                item: gettext('条记录'),
                comma: gettext('，'),
                currentPageTip: gettext('当前第'),
                page: gettext('页'),
                executing: gettext('执行中'),
                pauseState: gettext('暂停'),
                taskType: gettext('任务分类'),
                query: gettext('搜索'),
                reset: gettext('清空'),
                taskTypePlaceholder: gettext('请选择分类'),
                creatorPlaceholder: gettext('请输入创建人'),
                executorPlaceholder: gettext('请输入执行人'),
                statusPlaceholder: gettext('请选择状态')
            },
            taskBasicInfoLoading: true,
            listLoading: true,
            isAdvancedSerachShow: false,
            currentPage: 1,
            totalPage: 1,
            countPerPage: 15,
            totalCount: 0,
            taskSync: 0,
            statusSync: 0,
            searchStr: '',
            creator: undefined,
            executor: undefined,
            activeTaskCategory: undefined,
            executeStartTime: undefined,
            executeEndTime: undefined,
            isStarted: undefined,
            isFinished: undefined,
            auditList: [],
            statusList: [],
            taskCategory: [],
            executeStatus: [] // 任务执行态
        }
    },
    computed: {
    },
    created () {
        this.loadFunctionTask()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('auditTask/', [
            'loadAuditTaskList'
        ]),
        ...mapActions('task/', [
            'getInstanceStatus'
        ]),
        async loadFunctionTask () {
            this.listLoading = true
            try {
                const data = {
                    limit: this.countPerPage,
                    offset: (this.currentPage - 1) * this.countPerPage,
                    q: this.searchStr
                }
                const auditListData = await this.loadAuditTaskList(data)
                const list = auditListData.objects
                this.auditList = list
                this.totalCount = auditListData.meta.total_count
                const totalPage = Math.ceil( this.totalCount / this.countPerPage)
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
        onPageChange (page) {
            this.currentPage = page
            this.loadFunctionTask()
        },
        searchInputhandler () {
            this.currentPage = 1
            this.loadFunctionTask()
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
        onAdvanceShow () {
            this.isAdvancedSerachShow = !this.isAdvancedSerachShow
        },
        onChangeExecuteTime (oldValue, newValue) {
            const timeArray = newValue.split(" - ")
            this.executeStartTime = timeArray[0]
            this.executeEndTime = timeArray[1]
        },
        onClearCategory (){
            this.activeTaskCategory = undefined
        },
        onSelectedCategory () {
            this.activeTaskCategory = name
        }
    }
}
</script>
<style lang='scss'>
@import '@/scss/config.scss';
.audit-container {
    padding-top: 20px;
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: #fafafa;
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
    .advanced-search {
        margin: 20px 0px;
    }
}
.operation-area {
    margin: 20px 0;
    float: right;
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
.audit-fieldset {
    width: 100%;
    margin-bottom: 15px;
    border: 1px solid $commonBorderColor;
    background: #fff;
    .audit-query-content {
        display: flex;
        flex-wrap: wrap;
        .query-content {
            min-width: 420px;
            padding: 10px;
            @media screen and (max-width: 1420px){
                min-width: 380px;
            }
            .query-span {
                float: left;
                min-width: 130px;
                margin-right: 12px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                text-align: right;
                @media screen and (max-width: 1420px){
                    min-width: 100px;
                }
            }
            input {
                max-width: 260px;
                height: 32px;
                line-height: 32px;
            }
            .bk-date-range:after {
                height: 32px;
                line-height: 32px;
            }
            .bk-selector-icon.clear-icon {
                top:6px;
            }
            /deep/ .bk-selector {
                max-width: 260px;
                display: inline-block;
            }
            input::-webkit-input-placeholder{
                color: $formBorderColor;
            }
            input:-moz-placeholder {
                color: $formBorderColor;
            }
            input::-moz-placeholder {
                color: $formBorderColor;
            }
            input:-ms-input-placeholder {
                color: $formBorderColor;
            }
            input,.bk-selector,.bk-date-range {
                min-width: 260px;
            }
            .search-input {
                width: 260px;
                height: 32px;
                padding: 0 10px 0 10px;
                font-size: 14px;
                border: 1px solid $commonBorderColor;
                line-height: 32px;
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
            .bk-selector-search-item > input {
                min-width: 249px;
            }
            .bk-date-range {
                display: inline-block;
                width: 260px;
            }
        }
    }
}
.common-icon-dark-circle-pause {
    color: #FF9C01;
    font-size: 12px;
}
.audit-table-content {
    table {
        width: 100%;
        border: 1px solid $commonBorderColor;;
        border-collapse: collapse;
        font-size: 12px;
        background: $whiteDefault;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: #fafafa;
        }
        th,td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid $commonBorderColor;;
        }
        th {
            background: #fafafa;
        }
        .audit-id {
            width: 80px;
        }
        .audit-name {
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
        .audit-type {
            width: 110px;
        }
        .audit-time {
            width: 215px;
        }
        .audit-creator {
            width: 100px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .audit-business {
            width: 120px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .audit-status {
            width: 100px;
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
        .audit-operation {
            width: 90px;
        }
        .audit-category {
            width: 110px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .audit-executor {
            width: 100px;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
    }
    .btn-size-mini {
        height: 24px;
        line-height: 22px;
        padding: 0 11px;
        font-size: 12px;
    }
    .audit-operation-btn {
        color: #3c96ff;
    }
    .empty-data {
        padding: 120px 0;
    }
}
.panagation {
    margin-top: 20px;
    text-align: right;
    .page-info {
        float: left;
        margin-top: 10px;
        font-size: 14px;
    }
}
</style>

