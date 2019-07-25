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
            <BaseSearch
                v-model="searchStr"
                :input-placeholader="i18n.placeholder"
                @onShow="onAdvanceShow"
                @input="onSearchInput">
            </BaseSearch>
            <div class="audit-search" v-show="isAdvancedSerachShow">
                <fieldset class="audit-fieldset">
                    <div class="audit-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.business}}</span>
                            <bk-select
                                v-model="selectedCcId"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.choice"
                                :clearable="true"
                                @selected="onSelectedBizCcId">
                                <bk-option
                                    v-for="(option, index) in business.list"
                                    :key="index"
                                    :id="option.cc_id"
                                    :name="option.cc_name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.startedTime}}</span>
                            <bk-date-picker
                                ref="bkRanger"
                                :placeholder="i18n.dateRange"
                                :type="'daterange'"
                                @change="onChangeExecuteTime">
                            </bk-date-picker>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.taskType}}</span>
                            <bk-select
                                v-model="taskSync"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.taskTypePlaceholder"
                                :clearable="true"
                                @clear="onClearCategory"
                                @selected="onSelectedCategory">
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
                                :placeholder="i18n.statusPlaceholder"
                                :clearable="true"
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
            <div class="audit-table-content">
                <table v-bkloading="{ isLoading: listLoading, opacity: 1 }">
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
    import BaseSearch from '@/components/common/base/BaseSearch.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'

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
                    statusPlaceholder: gettext('请选择状态'),
                    dateRange: gettext('选择日期时间范围')
                },
                taskBasicInfoLoading: true,
                listLoading: true,
                isAdvancedSerachShow: false,
                currentPage: 1,
                selectedCcId: '',
                totalPage: 1,
                countPerPage: 15,
                totalCount: 0,
                taskSync: '',
                statusSync: '',
                searchStr: '',
                bizCcId: undefined,
                creator: undefined,
                executor: undefined,
                activeTaskCategory: undefined,
                executeStartTime: undefined,
                executeEndTime: undefined,
                isStarted: undefined,
                isFinished: undefined,
                business: {
                    list: [],
                    loading: false,
                    id: null,
                    searchable: true,
                    empty: false
                },
                auditList: [],
                taskCategory: [],
                statusList: [
                    { 'id': 'nonExecution', 'name': gettext('未执行') },
                    { 'id': 'runing', 'name': gettext('未完成') },
                    { 'id': 'finished', 'name': gettext('完成') }
                ],
                executeStatus: [] // 任务执行态
            }
        },
        created () {
            this.loadFunctionTask()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
            this.getBusinessList()
            this.getBusinessBaseInfo()
        },
        methods: {
            ...mapActions('auditTask/', [
                'loadAuditTaskList'
            ]),
            ...mapActions('functionTask/', [
                'loadFunctionBusinessList'
            ]),
            ...mapActions('task/', [
                'getInstanceStatus'
            ]),
            ...mapActions('template/', [
                'loadBusinessBaseInfo'
            ]),
            async loadFunctionTask () {
                this.listLoading = true
                try {
                    const data = {
                        limit: this.countPerPage,
                        offset: (this.currentPage - 1) * this.countPerPage,
                        business__cc_id: this.bizCcId,
                        category: this.activeTaskCategory,
                        audit__pipeline_instance__name__contains: this.searchStr,
                        pipeline_instance__is_started: this.isStarted,
                        pipeline_instance__is_finished: this.isFinished,
                        pipeline_instance__creator__contains: this.creator,
                        pipeline_instance__executor__contains: this.executor
                    }
                    if (this.executeEndTime) {
                        if (this.common) {
                            data['pipeline_template__start_time__gte'] = moment(this.executeStartTime).format('YYYY-MM-DD')
                            data['pipeline_template__start_time__lte'] = moment(this.executeEndTime).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['pipeline_instance__start_time__gte'] = moment.tz(this.executeStartTime, this.businessTimezone).format('YYYY-MM-DD')
                            data['pipeline_instance__start_time__lte'] = moment.tz(this.executeEndTime, this.businessTimezone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    const auditListData = await this.loadAuditTaskList(data)
                    const list = auditListData.objects
                    this.auditList = list
                    this.totalCount = auditListData.meta.total_count
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
            async getBusinessList () {
                this.business.loading = true
                try {
                    const businessData = await this.loadFunctionBusinessList()
                    this.business.list = businessData.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.business.loading = false
                }
            },
            async getBusinessBaseInfo () {
                this.taskBasicInfoLoading = true
                try {
                    const data = await this.loadBusinessBaseInfo()
                    this.taskCategory = data.task_categories.map(m => ({ name: m.name, id: m.value }))
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskBasicInfoLoading = false
                }
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onChangeExecuteTime (Value) {
                this.executeStartTime = Value[0]
                this.executeEndTime = Value[1]
            },
            onClearCategory () {
                this.activeTaskCategory = undefined
            },
            onSelectedCategory (id) {
                this.activeTaskCategory = id
            },
            onResetForm () {
                this.isStarted = undefined
                this.isFinished = undefined
                this.creator = undefined
                this.executor = undefined
                this.searchStr = undefined
                this.statusSync = ''
                this.selectedCcId = ''
                this.taskSync = ''
                this.activeTaskCategory = undefined
                this.executeStartTime = undefined
                this.executeEndTime = undefined
            },
            onSelectedStatus (id, name) {
                this.isStarted = id !== 'nonExecution'
                this.isFinished = id === 'finished'
            },
            onClearStatus () {
                this.isStarted = undefined
                this.isFinished = undefined
            },
            onSelectedBizCcId (name, value) {
                if (this.bizCcId === name) {
                    return
                }
                this.bizCcId = name
            }
        }
    }
</script>
<style lang='scss'>
@import '@/scss/config.scss';
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.audit-container {
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
    padding: 8px;
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
        .query-button {
            padding: 10px;
            min-width: 450px;
            @media screen and (max-width: 1420px) {
                min-width: 390px;
            }
            text-align: center;
            .query-cancel {
                margin-left: 5px;
            }
            .bk-button {
                height: 32px;
                line-height: 32px;
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
            padding: 11px;
            text-align: left;
            border-bottom: 1px solid $commonBorderColor;;
        }
        td {
            color: #63656e
        }
        th {
            background: #fafafa;
        }
        .audit-id {
            padding-left: 20px;
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
</style>
