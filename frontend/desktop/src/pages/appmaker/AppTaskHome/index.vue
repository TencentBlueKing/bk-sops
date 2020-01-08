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
    <div class="appmaker-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.taskRecord"></BaseTitle>
            <div class="operation-area clearfix">
                <div class="appmaker-search">
                    <AdvanceSearch
                        v-model="searchStr"
                        :input-placeholader="i18n.placeholder"
                        @onShow="onAdvanceShow"
                        @input="onSearchInput">
                    </AdvanceSearch>
                </div>
            </div>
            <div class="app-search" v-show="isAdvancedSerachShow">
                <fieldset class="task-fieldset">
                    <div class="task-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.startedTime}}</span>
                            <bk-date-picker
                                ref="bkRanger"
                                v-model="timeRange"
                                :placeholder="i18n.dateRange"
                                :type="'daterange'">
                            </bk-date-picker>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.task_type}}</span>
                            <bk-select
                                v-model="taskSync"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :is-loading="taskBasicInfoLoading"
                                :placeholder="i18n.taskTypePlaceholder"
                                @clear="onClearCategory">
                                <bk-option
                                    v-for="(option, index) in taskCategory"
                                    :key="index"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.creator}}</span>
                            <bk-input
                                v-model="creator"
                                class="bk-input-inline"
                                :clearable="true"
                                :placeholder="i18n.creatorPlaceholder">
                            </bk-input>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.operator}}</span>
                            <bk-input
                                v-model="executor"
                                class="bk-input-inline"
                                :clearable="true"
                                :placeholder="i18n.executorPlaceholder">
                            </bk-input>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.status}}</span>
                            <bk-select
                                v-model="statusSync"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :is-loading="taskBasicInfoLoading"
                                :placeholder="i18n.statusPlaceholder"
                                @clear="onClearStatus"
                                @selected="onSelectedStatus">
                                <bk-option
                                    v-for="(option, index) in statusList"
                                    :key="index"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="query-button">
                            <bk-button class="query-primary" theme="primary" @click="searchInputhandler">{{i18n.query}}</bk-button>
                            <bk-button class="query-cancel" @click="onResetForm">{{i18n.reset}}</bk-button>
                        </div>
                    </div>
                </fieldset>
            </div>
            <div class="appmaker-table-content">
                <bk-table
                    :data="appmakerList"
                    :pagination="pagination"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }"
                    @page-change="onPageChange">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="i18n.name">
                        <template slot-scope="props">
                            <router-link
                                class="task-name"
                                :title="props.row.name"
                                :to="`/appmaker/${props.row.create_info}/execute/${props.row.business.cc_id}/?instance_id=${props.row.id}`">
                                {{props.row.name}}
                            </router-link>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.startedTime" width="200">
                        <template slot-scope="props">
                            {{ props.row.start_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.finishedTime" width="200">
                        <template slot-scope="props">
                            {{ props.row.finish_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.category" prop="category_name" width="100"></bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator_name" width="100"></bk-table-column>
                    <bk-table-column :label="i18n.operator" width="100">
                        <template slot-scope="props">
                            {{ props.row.executor_name || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.status" width="100">
                        <template slot-scope="props">
                            <div class="appmaker-status">
                                <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                <span v-if="executeStatus[props.$index]">{{executeStatus[props.$index].text}}</span>
                            </div>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearch from '@/components/common/base/AdvanceSearch.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    export default {
        name: 'appmakerTaskHome',
        components: {
            CopyrightFooter,
            BaseTitle,
            AdvanceSearch,
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
                    taskRecord: gettext('任务记录'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    dateRange: gettext('选择日期时间范围'),
                    task_type: gettext('任务分类'),
                    creatorPlaceholder: gettext('请输入创建人'),
                    executorPlaceholder: gettext('请输入执行人'),
                    taskTypePlaceholder: gettext('请选择分类'),
                    statusPlaceholder: gettext('请选择状态')
                },
                listLoading: true,
                isDeleteDialogShow: false,
                taskBasicInfoLoading: true,
                isAdvancedSerachShow: false,
                theDeleteTemplateId: undefined,
                pending: {
                    delete: false,
                    authority: false
                },
                searchStr: '',
                taskSync: '',
                creator: '',
                executor: '',
                statusSync: '',
                isStarted: undefined,
                isFinished: undefined,
                appmakerList: [],
                executeStatus: [], // 任务执行状态
                taskCategory: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15],
                    'show-limit': false
                },
                timeRange: [],
                statusList: [
                    { 'id': 'nonExecution', 'name': gettext('未执行') },
                    { 'id': 'runing', 'name': gettext('未完成') },
                    { 'id': 'finished', 'name': gettext('完成') }
                ]
            }
        },
        computed: {
            ...mapState({
                businessTimezone: state => state.businessTimezone
            })
        },
        created () {
            this.getAppmakerList()
            this.getBizBaseInfo()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('taskList/', [
                'loadTaskList'
            ]),
            ...mapActions('task/', [
                'getInstanceStatus'
            ]),
            ...mapActions('template/', [
                'loadBusinessBaseInfo'
            ]),
            ...mapMutations('template/', [
                'setBusinessBaseInfo'
            ]),
            async getAppmakerList () {
                this.listLoading = true
                try {
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        create_method: 'app_maker',
                        create_info: this.app_id,
                        q: this.searchStr,
                        category: this.taskSync || undefined,
                        pipeline_instance__creator__contains: this.creator || undefined,
                        pipeline_instance__executor__contains: this.executor || undefined,
                        pipeline_instance__is_started: this.isStarted,
                        pipeline_instance__is_finished: this.isFinished
                    }

                    if (this.timeRange.length && this.timeRange.every(m => m !== '')) {
                        data['pipeline_instance__start_time__gte'] = moment.tz(this.timeRange[0], this.businessTimezone).format('YYYY-MM-DD')
                        data['pipeline_instance__start_time__lte'] = moment.tz(this.executeEndTime, this.businessTimezone).add('1', 'd').format('YYYY-MM-DD')
                    }

                    const appmakerListData = await this.loadTaskList(data)
                    const list = appmakerListData.objects
                    this.appmakerList = list
                    this.pagination.count = appmakerListData.meta.total_count
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
            async getBizBaseInfo () {
                try {
                    const bizBasicInfo = await this.loadBusinessBaseInfo()
                    this.taskCategory = bizBasicInfo.task_categories.map(m => ({ id: m.value, name: m.name }))
                    this.setBusinessBaseInfo(bizBasicInfo)
                    this.taskBasicInfoLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getAppmakerList()
            },
            onClearCategory () {
                this.activeTaskCategory = ''
            },
            searchInputhandler () {
                this.pagination.current = 1
                this.getAppmakerList()
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onClearStatus () {
                this.isStarted = undefined
                this.isFinished = undefined
            },
            onSelectedStatus (id) {
                this.isStarted = id !== 'nonExecution'
                this.isFinished = id === 'finished'
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
            },
            onResetForm () {
                this.timeRange = []
                this.taskSync = ''
                this.creator = ''
                this.executor = ''
                this.statusSync = ''
                this.isStarted = undefined
                this.isFinished = undefined
                this.getAppmakerList()
            }

        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/advancedSearch.scss';
.bk-select-inline,.bk-input-inline {
   display: inline-block;
    width: 260px;
}
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
    .advanced-search {
        margin: 0;
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
.app-search {
    @include advancedSearch;
}
.appmaker-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .appmaker-status {
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
    .empty-data {
        padding: 120px 0;
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
