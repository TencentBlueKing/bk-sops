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
    <div class="task-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.task_list"></BaseTitle>
            <div class="task-table-content">
                <div class="operation-area clearfix">
                    <bk-button
                        theme="primary"
                        class="task-btn"
                        @click="onCreateTask">
                        {{i18n.create}}
                    </bk-button>
                    <div class="task-advanced-search">
                        <BaseSearch
                            class="base-search"
                            v-model="flowName"
                            :input-placeholader="i18n.taskNamePlaceholder"
                            @onShow="onAdvanceShow"
                            @input="onSearchInput">
                        </BaseSearch>
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
                <table v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <thead>
                        <tr>
                            <th class="task-id">ID</th>
                            <th class="task-name">{{ i18n.task_name }}</th>
                            <th class="task-time">{{ i18n.start_time }}</th>
                            <th class="task-time">{{ i18n.finish_time }}</th>
                            <th class="task-type">{{ i18n.task_type }}</th>
                            <th class="task-executor">{{ i18n.creator }}</th>
                            <th class="task-executor">{{ i18n.executor }}</th>
                            <th class="task-method">{{ i18n.createMethod }}</th>
                            <th class="task-status">{{ i18n.status }}</th>
                            <th class="task-operation">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, index) in taskList" :key="item.id">
                            <td class="task-id">{{item.id}}</td>
                            <td class="task-name">
                                <router-link
                                    :title="item.name"
                                    :to="`/taskflow/execute/${cc_id}/?instance_id=${item.id}`">
                                    {{item.name}}
                                </router-link>
                            </td>
                            <td class="task-time">{{item.start_time || '--'}}</td>
                            <td class="task-time">{{item.finish_time || '--'}}</td>
                            <td class="task-type">{{item.category_name}}</td>
                            <td class="task-executor">{{item.creator_name}}</td>
                            <td class="task-executor">{{item.executor_name || '--'}}</td>
                            <td class="task-method">{{transformCreateMethod(item.create_method)}}</td>
                            <td class="task-status">
                                <span :class="executeStatus[index] && executeStatus[index].cls"></span>
                                <span v-if="executeStatus[index]">{{executeStatus[index].text}}</span>
                            </td>
                            <td class="task-operation">
                                <a class="task-operation-clone" href="javascript:void(0);" @click.prevent="onCloneTaskClick(item.id, item.name)">{{ i18n.clone }}</a>
                                <a class="task-operation-delete" href="javascript:void(0);" @click.prevent="onDeleteTask(item.id, item.name)">{{ i18n.delete }}</a>
                            </td>
                        </tr>
                        <tr v-if="!taskList || !taskList.length" class="empty-tr">
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
            v-if="isTaskCloneDialogShow"
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
            :header-position="'center'"
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
    import BaseSearch from '@/components/common/base/BaseSearch.vue'
    import TaskCreateDialog from './TaskCreateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import moment from 'moment-timezone'
    import TaskCloneDialog from './TaskCloneDialog.vue'

    export default {
        name: 'TaskList',
        components: {
            CopyrightFooter,
            BaseTitle,
            BaseSearch,
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
                currentPage: 1,
                totalPage: 1,
                countPerPage: 15,
                totalCount: 0,
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
                createMethod: this.create_method || ''
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
                        limit: this.countPerPage,
                        offset: (this.currentPage - 1) * this.countPerPage,
                        category: this.activeTaskCategory,
                        template_id: this.templateId,
                        common: this.common,
                        pipeline_instance__creator__contains: this.creator,
                        pipeline_instance__executor__contains: this.executor,
                        pipeline_instance__name__contains: this.flowName,
                        pipeline_instance__is_started: this.isStarted,
                        pipeline_instance__is_finished: this.isFinished,
                        create_method: this.createMethod || this.create_method || undefined
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
                    this.totalCount = taskListData.meta.total_count
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
                this.currentPage = 1
                this.getTaskList()
            },
            searchInputhandler () {
                this.currentPage = 1
                this.getTaskList()
            },
            onDeleteTask (id, name) {
                console.log('zhixing')
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
                    this.isDeleteDialogShow = false
                    // 最后一页最后一条删除后，往前翻一页
                    if (
                        this.currentPage > 1
                        && this.totalPage === this.currentPage
                        && this.totalCount - (this.totalPage - 1) * this.countPerPage === 1
                    ) {
                        this.currentPage -= 1
                    }
                    await this.getTaskList()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
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
                this.currentPage = page
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
.task-container {
    .dialog-content {
        word-break: break-all;
    }
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
.task-fieldset {
    width: 100%;
    margin-bottom: 15px;
    padding: 8px;
    border: 1px solid $commonBorderColor;
    background: #fff;
    .task-query-content {
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
                top:7px;
            }
            /deep/ .bk-selector {
                max-width: 260px;
                display: inline-block;
            }
            /deep/ .bk-date-range input {
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
            .bk-selector-search-item > input {
                min-width: 249px;
            }
            .bk-date-range {
                display: inline-block;
                width: 260px;
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
            .search-input.placeholder {
                color: $formBorderColor;
            }
        }
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
.common-icon-dark-circle-pause {
    color: #FF9C01;
    font-size: 12px;
}
.task-table-content {
    .bk-button {
        min-width: 120px;
    }
    table {
        width: 100%;
        border: 1px solid $commonBorderColor;
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
            background: $whiteNodeBg;
        }
        .task-id {
            padding-left: 20px;
            width: 80px;
        }
        .task-name {
            text-align: left;
            a {
                display: block;
                width: 100%;
                color: $blueDefault;
                text-overflow: ellipsis;
                white-space: nowrap;
                word-break: break-all;
                overflow: hidden;
            }
        }
        @media screen and (min-width: 1500px) {
            .task-time {
                width: 220px;
            }
        }
        @media screen and (max-width: 1500px) {
            .task-time {
                width: 152px;
            }
            td[class="task-time"] {
                height: 60px;
            }
        }
        .task-type {
            width: 122px;
        }
        .task-executor {
            width: 110px;
            text-overflow: ellipsis;
            white-space: nowrap;
            word-break: break-all;
            overflow: hidden;
        }
        .task-method {
            width: 120px;
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
                font-size: 14px;
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
