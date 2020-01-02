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
    <div class="task-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.task_list"></BaseTitle>
            <div class="operation-area">
                <div class="operation-area clearfix">
                    <bk-button
                        theme="primary"
                        class="task-btn"
                        @click="onCreateTask">
                        {{i18n.create}}
                    </bk-button>
                    <div class="task-advanced-search">
                        <AdvanceSearch
                            class="base-search"
                            v-model="flowName"
                            :input-placeholader="i18n.taskNamePlaceholder"
                            @onShow="onAdvanceShow"
                            @input="onSearchInput">
                        </AdvanceSearch>
                    </div>
                </div>
            </div>
            <div class="task-search" v-show="isAdvancedSerachShow">
                <fieldset class="task-fieldset">
                    <div class="task-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.start_time}}</span>
                            <bk-date-picker
                                ref="bkRanger"
                                v-model="TimeRange"
                                :placeholder="i18n.dateRange"
                                :type="'daterange'"
                                @change="onChangeExecuteTime">
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
                            <span class="query-span">{{i18n.createMethod}}</span>
                            <bk-select
                                v-model="createMethod"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :is-loading="taskBasicInfoLoading"
                                :placeholder="i18n.createMethodPlaceholder"
                                @clear="onClearCreateMethod"
                                @selected="onSelectedCreateMethod">
                                <bk-option
                                    v-for="(option, index) in taskCreateMethodList"
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
                            <span class="query-span">{{i18n.executor}}</span>
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
            <div class="task-table-content">
                <bk-table
                    :data="taskList"
                    :pagination="pagination"
                    @page-change="onPageChange"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="i18n.task_name" prop="name">
                        <template slot-scope="props">
                            <router-link
                                class="task-name"
                                :title="props.row.name"
                                :to="`/taskflow/execute/${cc_id}/?instance_id=${props.row.id}`">
                                {{ props.row.name }}
                            </router-link>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.start_time" prop="category_name">
                        <template slot-scope="props">
                            {{ props.row.start_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.finish_time">
                        <template slot-scope="props">
                            {{ props.row.finish_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.task_type" prop="category_name"></bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator_name" width="120"></bk-table-column>
                    <bk-table-column :label="i18n.executor" width="100">
                        <template slot-scope="props">
                            {{ props.row.executor_name || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.createMethod" width="80">
                        <template slot-scope="props">
                            {{ transformCreateMethod(props.row.create_method) }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.status" width="120">
                        <template slot-scope="props">
                            <div class="task-status">
                                <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.operation" width="120">
                        <template slot-scope="props">
                            <div class="task-operation">
                                <a
                                    class="task-operation-clone"
                                    href="javascript:void(0);"
                                    @click.prevent="onCloneTaskClick(props.row.id, props.row.name)">
                                    {{ i18n.clone }}
                                </a>
                                <a
                                    class="task-operation-delete"
                                    href="javascript:void(0);"
                                    @click.prevent="onDeleteTask(props.row.id, props.row.name)">
                                    {{ i18n.delete }}
                                </a>
                            </div>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="i18n.empty" /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <TaskCreateDialog
            :common="common"
            :cc_id="cc_id"
            :is-new-task-dialog-show="isNewTaskDialogShow"
            :business-info-loading="businessInfoLoading"
            :create-entrance="true"
            :task-category="taskCategory"
            @onCreateTaskCancel="onCreateTaskCancel">
        </TaskCreateDialog>
        <TaskCloneDialog
            :is-task-clone-dialog-show="isTaskCloneDialogShow"
            :task-name="theCloneTaskName"
            :pending="pending.clone"
            @confirm="onCloneConfirm"
            @cancel="onCloneCancel">
        </TaskCloneDialog>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.delete"
            :value="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div class="dialog-content" v-bkloading="{ isLoading: pending.delete, opacity: 1 }">
                {{i18n.deleleTip + '"' + theDeleteTaskName + '"?'}}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearch from '@/components/common/base/AdvanceSearch.vue'
    import TaskCreateDialog from './TaskCreateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import moment from 'moment-timezone'
    import TaskCloneDialog from './TaskCloneDialog.vue'
    export default {
        name: 'TaskList',
        components: {
            CopyrightFooter,
            BaseTitle,
            AdvanceSearch,
            NoData,
            TaskCreateDialog,
            TaskCloneDialog
        },
        props: ['cc_id', 'common', 'create_method'],
        data () {
            return {
                listLoading: true,
                templateId: this.$route.query.template_id,
                taskCategory: [],
                activeTaskCategory: undefined, // 任务类型筛选
                searchStr: '',
                executeStatus: [], // 任务执行状态
                TimeRange: ['', ''],
                totalPage: 1,
                isDeleteDialogShow: false,
                shapeShow: false,
                isAdvancedSerachShow: false,
                theDeleteTaskId: undefined,
                theDeleteTaskName: '',
                isTaskCloneDialogShow: false,
                isNewTaskDialogShow: false,
                businessInfoLoading: true, // 模板分类信息 loading
                theCloneTaskName: '',
                theCloneTaskId: undefined,
                pending: {
                    delete: false,
                    clone: false
                },
                i18n: {
                    allCategory: gettext('全部'),
                    placeholder: gettext('请输入ID或任务名称'),
                    task_list: gettext('任务记录'),
                    task_name: gettext('任务名称'),
                    start_time: gettext('执行开始'),
                    finish_time: gettext('执行结束'),
                    task_type: gettext('任务分类'),
                    creator: gettext('创建人'),
                    executor: gettext('执行人'),
                    status: gettext('状态'),
                    operation: gettext('操作'),
                    clone: gettext('克隆'),
                    delete: gettext('删除'),
                    deleleTip: gettext('确认删除'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    taskNamePlaceholder: gettext('请输入任务名称'),
                    taskTypePlaceholder: gettext('请选择分类'),
                    creatorPlaceholder: gettext('请输入创建人'),
                    executorPlaceholder: gettext('请输入执行人'),
                    statusPlaceholder: gettext('请选择状态'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    createMethod: gettext('创建方式'),
                    createMethodApp: gettext('应用内'),
                    createMethodAppmaker: gettext('轻应用'),
                    createMethodPlaceholder: gettext('请选择创建方式'),
                    advanceSearch: gettext('高级搜索'),
                    executing: gettext('执行中'),
                    pauseState: gettext('暂停'),
                    create: gettext('新建'),
                    dateRange: gettext('选择日期时间范围')
                },
                executeStartTime: undefined,
                executeEndTime: undefined,
                flowName: undefined,
                category: undefined,
                creator: undefined,
                executor: undefined,
                taskSync: '',
                statusList: [
                    { 'id': 'nonExecution', 'name': gettext('未执行') },
                    { 'id': 'runing', 'name': gettext('未完成') },
                    { 'id': 'finished', 'name': gettext('完成') }
                ],
                taskBasicInfoLoading: true,
                isStarted: undefined,
                isFinished: undefined,
                statusSync: '',
                taskCreateMethodList: [],
                createMethod: this.create_method || '',
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15],
                    'show-limit': false
                }
            }
        },
        computed: {
            ...mapState({
                taskList: state => state.taskList.taskListData,
                businessTimezone: state => state.businessTimezone
            })
        },
        created () {
            this.getData()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('template/', [
                'loadBusinessBaseInfo'
            ]),
            ...mapActions('task/', [
                'getInstanceStatus',
                'loadCreateMethod'
            ]),
            ...mapActions('taskList/', [
                'loadTaskList',
                'deleteTask',
                'cloneTask'
            ]),
            ...mapMutations('template/', [
                'setBusinessBaseInfo'
            ]),
            ...mapMutations('taskList/', [
                'setTaskListData'
            ]),
            async getTaskList () {
                // 空字符串需要转换为undefined，undefined数据在axios请求发送过程中会被删除
                if (this.executeStartTime === '') {
                    this.executeStartTime = undefined
                }
                this.listLoading = true
                this.executeStatus = []
                try {
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        category: this.activeTaskCategory,
                        template_id: this.templateId,
                        common: this.common,
                        pipeline_instance__creator__contains: this.creator,
                        pipeline_instance__executor__contains: this.executor,
                        pipeline_instance__name__contains: this.flowName,
                        pipeline_instance__is_started: this.isStarted,
                        pipeline_instance__is_finished: this.isFinished,
                        create_method: this.createMethod || undefined
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
                    const taskListData = await this.loadTaskList(data)
                    const list = taskListData.objects
                    this.pagination.count = taskListData.meta.total_count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
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
                    this.setTaskListData(list)
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
                                status.cls = 'execute common-icon-dark-circle-pause'
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
            onCategoryClick (category) {
                this.activeTaskCategory = category
                this.pagination.current = 1
                this.getTaskList()
            },
            searchInputhandler () {
                this.pagination.current = 1
                this.getTaskList()
            },
            onDeleteTask (id, name) {
                this.theDeleteTaskId = id
                this.theDeleteTaskName = name
                this.isDeleteDialogShow = true
            },
            async onDeleteConfirm () {
                if (this.pending.delete) return
                this.pending.delete = true
                try {
                    await this.deleteTask(this.theDeleteTaskId)
                    this.theDeleteTaskId = undefined
                    this.theDeleteTaskName = ''
                    // 最后一页最后一条删除后，往前翻一页
                    if (
                        this.pagination.current > 1
                        && this.totalPage === this.pagination.current
                        && this.pagination.count - (this.totalPage - 1) * this.pagination.limit === 1
                    ) {
                        this.pagination.current -= 1
                    }
                    await this.getTaskList()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isDeleteDialogShow = false
                    this.pending.delete = false
                }
            },
            onDeleteCancel () {
                this.theDeleteTaskId = undefined
                this.theDeleteTaskName = ''
                this.isDeleteDialogShow = false
            },
            onCloneTaskClick (id, name) {
                this.isTaskCloneDialogShow = true
                this.theCloneTaskId = id
                this.theCloneTaskName = name
            },
            async onCloneConfirm (name) {
                if (this.pending.clone) return
                this.pending.clone = true
                const config = {
                    name,
                    task_id: this.theCloneTaskId
                }
                try {
                    const data = await this.cloneTask(config)
                    this.$router.push({ path: `/taskflow/execute/${this.cc_id}/`, query: { instance_id: data.data.new_instance_id } })
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onCloneCancel () {
                this.isTaskCloneDialogShow = false
                this.theCloneTaskName = ''
            },
            onClearCategory () {
                this.activeTaskCategory = undefined
            },
            onSelectedCategory (name, value) {
                this.activeTaskCategory = name
            },
            onSelectedCreateMethod (value) {
                this.createMethod = value
            },
            onSelectedStatus (id) {
                this.isStarted = id !== 'nonExecution'
                this.isFinished = id === 'finished'
            },
            onClearCreateMethod () {
                this.createMethod = ''
            },
            onClearStatus () {
                this.isStarted = undefined
                this.isFinished = undefined
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getTaskList()
            },
            onResetForm () {
                this.TimeRange = ['', '']
                this.isStarted = undefined
                this.isFinished = undefined
                this.createMethod = ''
                this.creator = undefined
                this.executor = undefined
                this.flowName = undefined
                this.statusSync = ''
                this.taskSync = ''
                this.executeStartTime = undefined
                this.executeEndTime = undefined
                this.searchInputhandler()
            },
            onChangeExecuteTime (oldValue, newValue) {
                // const timeArray = oldValue.split(' - ')
                this.executeStartTime = oldValue[0]
                this.executeEndTime = oldValue[1]
            },
            async getCreateMethod () {
                try {
                    const createMethodData = await this.loadCreateMethod()
                    this.taskCreateMethodList = createMethodData.data.map(m => ({ id: m.value, name: m.name }))
                    this.createMethod = this.create_method || ''
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getData () {
                Promise.all([
                    this.getTaskList(),
                    this.getCreateMethod(),
                    this.getBizBaseInfo()
                ]).catch(e => {
                    errorHandler(e, this)
                })
            },
            transformCreateMethod (value) {
                if (this.taskCreateMethodList.length === 0) {
                    return ''
                }
                const taskCreateMethod = this.taskCreateMethodList.find((taskCreateMethod) => taskCreateMethod['id'] === value)
                return taskCreateMethod['name']
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onCreateTask () {
                this.isNewTaskDialogShow = true
            },
            onCreateTaskCancel () {
                this.isNewTaskDialogShow = false
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/advancedSearch.scss';
@include advancedSearch;
.dialog-content {
    padding: 30px;
    word-break: break-all;
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
    .template-btn {
        margin-left: 5px;
        color: #313238;
    }
    .task-advanced-search {
        float: right;
        .base-search {
            margin: 0px;
        }
    }
}
.bk-select-inline {
    width: 260px;
    display: inline-block;
}
.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.common-icon-dark-circle-pause {
    color: #ff9c01;
    font-size: 14px;
}
.operation-area {
    .bk-button {
        min-width: 120px;
    }
}
.task-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .task-status {
        width: 105px;
        text-align: left;
        .common-icon-dark-circle-shape {
            display: inline-block;
            font-size: 14px;
            color: #979BA5;
            vertical-align: middle;
        }
        .common-icon-dark-circle-ellipsis {
            color: #3c96ff;
            font-size: 14px;
            vertical-align: middle;
        }
        .icon-check-circle-shape {
            font-size: 14px;
            color: $greenDefault;
            vertical-align: middle;
        }
        .common-icon-dark-circle-close {
            color: $redDefault;
            font-size: 16px;
            vertical-align: middle;
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
        .task-status-text {
            display: inline-block;
            vertical-align: middle;
        }
    }
    .task-operation {
        width: 150px;
        .task-operation-clone {
            color: #3C96FF;
            font-size: 12px;
        }
        .task-operation-delete {
            padding: 5px;
            color: #3C96FF;
            font-size: 12px;
        }
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
</style>
