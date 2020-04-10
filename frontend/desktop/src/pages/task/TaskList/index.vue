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
            <div class="operation-area">
                <advance-search-form
                    :search-config="{ placeholder: i18n.taskNamePlaceholder }"
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            theme="primary"
                            class="task-btn"
                            @click="onCreateTask">
                            {{i18n.create}}
                        </bk-button>
                    </template>
                </advance-search-form>
            </div>
            <div class="task-table-content">
                <bk-table
                    :data="taskList"
                    :pagination="pagination"
                    @page-change="onPageChange"
                    @page-limit-change="handlePageLimitChange"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <bk-table-column label="ID" prop="id" width="110"></bk-table-column>
                    <bk-table-column :label="i18n.task_name" prop="name" min-width="200">
                        <template slot-scope="props">
                            <a
                                v-if="!hasPermission(['view'], props.row.auth_actions, taskOperations)"
                                v-cursor
                                class="text-permission-disable"
                                :title="props.row.name"
                                @click="onTaskPermissonCheck(['view'], props.row, $event)">
                                {{props.row.name}}
                            </a>
                            <router-link
                                v-else
                                class="template-operate-btn"
                                :title="props.row.name"
                                :to="{
                                    name: 'taskExecute',
                                    params: { project_id: project_id },
                                    query: { instance_id: props.row.id }
                                }">
                                {{props.row.name}}
                            </router-link>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.start_time" prop="start_time" width="200">
                        <template slot-scope="props">
                            {{ props.row.start_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.finish_time" width="200">
                        <template slot-scope="props">
                            {{ props.row.finish_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.task_type" prop="category_name" width="100"></bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator_name" width="120">
                        <template slot-scope="props">
                            <span :title="props.row.creator_name">{{ props.row.creator_name }}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.executor" width="120">
                        <template slot-scope="props">
                            <span :title="props.row.executor_name || '--'">{{ props.row.executor_name || '--' }}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.createMethod" width="100">
                        <template slot-scope="props">
                            {{ transformCreateMethod(props.row.create_method) }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.status" width="100">
                        <template slot-scope="props">
                            <div class="task-status">
                                <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.operation" width="190">
                        <template slot-scope="props">
                            <div class="task-operation">
                                <!-- 事后鉴权，后续对接新版权限中心 -->
                                <router-link
                                    class="template-operate-btn"
                                    :to="{
                                        name: 'taskStep',
                                        query: { template_id: props.row.template_id },
                                        params: { project_id: project_id, step: 'selectnode' }
                                    }">
                                    {{i18n.recreate}}
                                </router-link>
                                <a
                                    v-cursor="{ active: !hasPermission(['clone'], props.row.auth_actions, taskOperations) }"
                                    :class="['task-operation-clone', {
                                        'text-permission-disable': !hasPermission(['clone'], props.row.auth_actions, taskOperations)
                                    }]"
                                    href="javascript:void(0);"
                                    @click="onCloneTaskClick(props.row, $event)">
                                    {{ i18n.clone }}
                                </a>
                                <a
                                    v-cursor="{ active: !hasPermission(['delete'], props.row.auth_actions, taskOperations) }"
                                    :class="['task-operation-delete', {
                                        'text-permission-disable': !hasPermission(['delete'], props.row.auth_actions, taskOperations)
                                    }]"
                                    href="javascript:void(0);"
                                    @click="onDeleteTask(props.row, $event)">
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
            :entrance="'taskflow'"
            :common="common"
            :project_id="project_id"
            :is-new-task-dialog-show="isNewTaskDialogShow"
            :business-info-loading="businessInfoLoading"
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
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import TaskCreateDialog from './TaskCreateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import moment from 'moment-timezone'
    import TaskCloneDialog from './TaskCloneDialog.vue'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'
    const searchForm = [
        {
            type: 'dateRange',
            key: 'executeTime',
            placeholder: gettext('选择日期时间范围'),
            label: gettext('执行开始'),
            value: []
        },
        {
            type: 'select',
            label: gettext('任务分类'),
            key: 'category',
            loading: false,
            placeholder: gettext('请选择分类'),
            list: []
        },
        {
            type: 'select',
            label: gettext('创建方式'),
            key: 'createMethod',
            loading: false,
            placeholder: gettext('请选择创建方式'),
            list: []
        },
        {
            type: 'input',
            key: 'creator',
            label: gettext('创建人'),
            placeholder: gettext('请输入创建人'),
            value: ''
        },
        {
            type: 'input',
            key: 'executor',
            label: gettext('执行人'),
            placeholder: gettext('请输入执行人'),
            value: ''
        },
        {
            type: 'select',
            label: gettext('状态'),
            key: 'statusSync',
            loading: false,
            placeholder: gettext('请选择状态'),
            list: [
                { 'value': 'nonExecution', 'name': gettext('未执行') },
                { 'value': 'runing', 'name': gettext('未完成') },
                { 'value': 'finished', 'name': gettext('完成') }
            ]
        }
    ]
    export default {
        name: 'TaskList',
        components: {
            CopyrightFooter,
            NoData,
            TaskCreateDialog,
            TaskCloneDialog,
            AdvanceSearchForm
        },
        mixins: [permission, task],
        props: {
            project_id: {
                type: [String, Number],
                default: ''
            },
            common: {
                type: String,
                default: ''
            },
            create_method: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                listLoading: true,
                templateId: this.$route.query.template_id,
                taskCategory: [],
                searchStr: '',
                executeStatus: [], // 任务执行状态
                totalPage: 1,
                isDeleteDialogShow: false,
                shapeShow: false,
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
                taskOperations: [],
                taskResource: {},
                i18n: {
                    allCategory: gettext('全部'),
                    placeholder: gettext('请输入ID或任务名称'),
                    task_name: gettext('任务名称'),
                    start_time: gettext('执行开始'),
                    finish_time: gettext('执行结束'),
                    task_type: gettext('任务分类'),
                    creator: gettext('创建人'),
                    executor: gettext('执行人'),
                    status: gettext('状态'),
                    operation: gettext('操作'),
                    recreate: gettext('再创建'),
                    clone: gettext('克隆'),
                    delete: gettext('删除'),
                    deleleTip: gettext('确认删除'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    taskNamePlaceholder: gettext('请输入任务名称'),
                    createMethod: gettext('创建方式'),
                    createMethodApp: gettext('应用内'),
                    createMethodAppmaker: gettext('轻应用'),
                    advanceSearch: gettext('高级搜索'),
                    executing: gettext('执行中'),
                    pauseState: gettext('暂停'),
                    create: gettext('新建')
                },
                taskBasicInfoLoading: true,
                taskCreateMethodList: [],
                createMethod: this.create_method || '',
                requestData: {
                    executeTime: [],
                    category: '',
                    createMethod: '',
                    creator: '',
                    executor: '',
                    statusSync: '',
                    flowName: ''
                },
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
                }
            }
        },
        computed: {
            ...mapState({
                taskList: state => state.taskList.taskListData
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone
            }),
            searchForm () {
                const value = searchForm
                // 任务执行
                value[1].list = this.taskCategory
                value[1].loading = this.taskBasicInfoLoading
                // 创建方式
                value[2].list = this.taskCreateMethodList
                value[5].loading = this.taskBasicInfoLoading
                return searchForm
            }
        },
        created () {
            this.getData()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('template/', [
                'loadProjectBaseInfo'
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
                'setProjectBaseInfo'
            ]),
            ...mapMutations('taskList/', [
                'setTaskListData'
            ]),
            async getTaskList () {
                // 空字符串需要转换为undefined，undefined数据在axios请求发送过程中会被删除
                this.listLoading = true
                this.executeStatus = []
                try {
                    const { executeTime, category, createMethod, creator, executor, statusSync, flowName } = this.requestData
                    let pipeline_instance__is_started
                    let pipeline_instance__is_finished
                    if (statusSync) {
                        pipeline_instance__is_started = statusSync !== 'nonExecution'
                        pipeline_instance__is_finished = statusSync === 'finished'
                    }
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        category: category || undefined,
                        template_id: this.templateId,
                        pipeline_instance__creator__contains: creator || undefined,
                        pipeline_instance__executor__contains: executor || undefined,
                        pipeline_instance__name__contains: flowName || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        create_method: createMethod || undefined,
                        project__id: this.project_id
                    }

                    if (executeTime[0] && executeTime[1]) {
                        if (this.common) {
                            data['pipeline_template__start_time__gte'] = moment(executeTime[0]).format('YYYY-MM-DD')
                            data['pipeline_template__start_time__lte'] = moment(executeTime[1]).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['pipeline_instance__start_time__gte'] = moment.tz(executeTime[0], this.timeZone).format('YYYY-MM-DD')
                            data['pipeline_instance__start_time__lte'] = moment.tz(executeTime[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    const taskListData = await this.loadTaskList(data)
                    const list = taskListData.objects
                    this.pagination.count = taskListData.meta.total_count
                    this.totalCount = taskListData.meta.total_count
                    this.taskOperations = taskListData.meta.auth_operations
                    this.taskResource = taskListData.meta.auth_resource
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', list)
                    this.setTaskListData(list)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.listLoading = false
                }
            },
            async getBizBaseInfo () {
                try {
                    const projectBasicInfo = await this.loadProjectBaseInfo()
                    this.taskCategory = projectBasicInfo.task_categories
                    this.setProjectBaseInfo(projectBasicInfo)
                    this.taskBasicInfoLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.getTaskList()
            },
            /**
             * 单个任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} task 任务数据对象
             * @params {Object} event 事件对象
             */
            onTaskPermissonCheck (required, task, event) {
                this.applyForPermission(required, task, this.taskOperations, this.taskResource)
                event.preventDefault()
            },
            onDeleteTask (task, event) {
                if (!this.hasPermission(['delete'], task.auth_actions, this.taskOperations)) {
                    this.onTaskPermissonCheck(['delete'], task, event)
                    return
                }
                this.theDeleteTaskId = task.id
                this.theDeleteTaskName = task.name
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
            onCloneTaskClick (task, event) {
                if (!this.hasPermission(['clone'], task.auth_actions, this.taskOperations)) {
                    this.onTaskPermissonCheck(['clone'], task, event)
                    return
                }
                this.isTaskCloneDialogShow = true
                this.theCloneTaskId = task.id
                this.theCloneTaskName = task.name
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
                    this.$router.push({
                        name: 'taskExecute',
                        params: { project_id: this.project_id },
                        query: { instance_id: data.data.new_instance_id }
                    })
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onCloneCancel () {
                this.isTaskCloneDialogShow = false
                this.theCloneTaskName = ''
            },
            onSelectedStatus (id) {
                this.isStarted = id !== 'nonExecution'
                this.isFinished = id === 'finished'
            },
            onClearStatus () {
                this.isStarted = undefined
                this.isFinished = undefined
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getTaskList()
            },
            async getCreateMethod () {
                try {
                    const createMethodData = await this.loadCreateMethod()
                    this.taskCreateMethodList = createMethodData.data.map(m => ({ value: m.value, name: m.name }))
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
                const taskCreateMethod = this.taskCreateMethodList.find((taskCreateMethod) => taskCreateMethod['value'] === value)
                return taskCreateMethod['name']
            },
            onCreateTask () {
                this.isNewTaskDialogShow = true
            },
            onCreateTaskCancel () {
                this.isNewTaskDialogShow = false
            },
            onSearchFormSubmit (data) {
                this.requestData = data
                this.getTaskList()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getTaskList()
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/advancedSearch.scss';
@import '@/scss/task.scss';
@include advancedSearch;
.dialog-content {
    padding: 30px;
    word-break: break-all;
}
.list-wrapper {
    min-height: calc(100vh - 300px);
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
    vertical-align: middle;
}
.task-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .task-status {
       @include ui-task-status;
    }
    .task-operation {
        .task-operation-clone {
            padding: 5px;
            color: #3a84ff;
            font-size: 12px;
        }
        .task-operation-delete {
            padding: 5px;
            color: #3a84ff;
            font-size: 12px;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
    .template-operate-btn {
        color: $blueDefault;
    }
}
</style>
