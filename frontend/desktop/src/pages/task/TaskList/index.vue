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
    <div class="task-container">
        <div class="task-create-method-tabs">
            <div
                v-for="method in createMethodTabs"
                :class="['create-method-tab-item', { active: crtCreateMethodTab === method.id }]"
                :key="method.id"
                @click="handleCreateMethodTabClick(method.id)">
                {{ method.name }}
            </div>
        </div>
        <div class="task-content-wrapper">
            <skeleton :loading="firstLoading" loader="taskList">
                <div class="list-wrapper">
                    <div class="search-wrapper mb20">
                        <bk-button
                            theme="primary"
                            style="min-width: 120px;"
                            data-test-id="taskList_form_createTask"
                            @click="onCreateTask">
                            {{$t('新建')}}
                        </bk-button>
                        <search-select
                            ref="searchSelect"
                            id="taskList"
                            :placeholder="$t('ID/任务名/创建人/执行人/状态/创建方式/执行代理人')"
                            v-model="searchSelectValue"
                            :search-list="searchList"
                            @change="handleSearchValueChange">
                        </search-select>
                    </div>
                    <div class="task-table-content" data-test-id="taskList_table_taskList">
                        <bk-table
                            ref="templateTable"
                            :data="taskList"
                            :pagination="pagination"
                            :size="setting.size"
                            v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }"
                            @page-change="onPageChange"
                            @page-limit-change="onPageLimitChange">
                            <bk-table-column
                                v-for="item in setting.selectedFields"
                                :key="item.id"
                                :label="item.label"
                                :prop="item.id"
                                :render-header="renderTableHeader"
                                :width="item.width"
                                :min-width="item.min_width">
                                <template slot-scope="props">
                                    <!--任务名称-->
                                    <div v-if="item.id === 'id'">
                                        <span v-if="props.row.isHasChild" :style="{ 'margin-left': `${(props.row.level - 1) * 30}px` }">
                                            <i
                                                :class="['commonicon-icon', 'common-icon-next-triangle-shape', props.row.isOpen ? 'show-chd' : 'close-chd']"
                                                @click="getCurProcessChdProcess(props.row)">
                                            </i>
                                        </span>
                                        <span v-else :style="{ 'margin-left': `${(props.row.level - 1) * 30}px` }"></span>
                                        <span>{{ props.row[item.id] || '--' }}</span>
                                    </div>
                                    <div v-else-if="item.id === 'name'">
                                        <a
                                            v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            :title="props.row.name"
                                            @click="onTaskPermissonCheck(['task_view'], props.row)">
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
                                    </div>
                                    <!--创建方式-->
                                    <div v-else-if="item.id === 'create_method'">
                                        {{ transformCreateMethod(props.row.create_method) }}
                                    </div>
                                    <!--状态-->
                                    <div v-else-if="item.id === 'task_status'" class="task-status">
                                        <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                        <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                                    </div>
                                    <!-- 其他 -->
                                    <template v-else>
                                        <span :title="props.row[item.id] || '--'">{{ props.row[item.id] || '--' }}</span>
                                    </template>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('操作')" width="190" :fixed="taskList.length ? 'right' : false">
                                <template slot-scope="props">
                                    <div class="task-operation">
                                        <!-- 事后鉴权，后续对接新版权限中心 -->
                                        <a v-if="props.row.template_deleted || props.row.template_source === 'onetime'" class="task-operation-btn disabled" data-test-id="taskList_table_recreateBtn">{{$t('再创建')}}</a>
                                        <a
                                            v-else-if="!hasCreateTaskPerm(props.row)"
                                            v-cursor
                                            class="text-permission-disable task-operation-btn"
                                            data-test-id="taskList_table_recreateBtn"
                                            @click="onTaskPermissonCheck([props.row.template_source === 'project' ? 'flow_create_task' : 'common_flow_create_task'], props.row)">
                                            {{$t('再创建')}}
                                        </a>
                                        <a
                                            v-else
                                            class="task-operation-btn"
                                            data-test-id="taskList_table_recreateBtn"
                                            @click="getCreateTaskUrl(props.row)">
                                            {{$t('再创建')}}
                                        </a>
                                        <a
                                            v-cursor="{ active: !hasPermission(['task_clone'], props.row.auth_actions) }"
                                            :class="['task-operation-btn', {
                                                'text-permission-disable': !hasPermission(['task_clone'], props.row.auth_actions)
                                            }]"
                                            href="javascript:void(0);"
                                            data-test-id="taskList_table_cloneBtn"
                                            @click="onCloneTaskClick(props.row, $event)">
                                            {{ $t('克隆') }}
                                        </a>
                                        <a
                                            v-cursor="{ active: !hasPermission(['task_delete'], props.row.auth_actions) }"
                                            :class="['task-operation-btn', {
                                                'text-permission-disable': !hasPermission(['task_delete'], props.row.auth_actions)
                                            }]"
                                            href="javascript:void(0);"
                                            data-test-id="taskList_table_deleteBtn"
                                            @click="onDeleteTask(props.row, $event)">
                                            {{ $t('删除') }}
                                        </a>
                                    </div>
                                </template>
                            </bk-table-column>
                            <bk-table-column type="setting">
                                <bk-table-setting-content
                                    :fields="setting.fieldList"
                                    :selected="setting.selectedFields"
                                    :size="setting.size"
                                    @setting-change="handleSettingChange">
                                </bk-table-setting-content>
                            </bk-table-column>
                            <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
                        </bk-table>
                    </div>
                </div>
            </skeleton>
        </div>
        <TaskCreateDialog
            :entrance="'taskflow'"
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
            :title="$t('删除')"
            :value="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div class="dialog-content" v-bkloading="{ isLoading: pending.delete, opacity: 1, zIndex: 100 }">
                {{$t('确认删除') + '"' + theDeleteTaskName + '"?'}}
            </div>
        </bk-dialog>
        <bk-dialog
            width="480"
            ext-cls="recreate-dialog"
            :value="isCreateDialogShow"
            theme="primary"
            :mask-close="false"
            :header-position="'left'"
            :title="$t('再创建')"
            :ok-text="$t('再创建')"
            @confirm="onCreateConfirm"
            @cancel="isCreateDialogShow = false">
            <bk-alert type="info" :title="$t('使用流程的最新数据再次创建任务，可重用当前参数')"></bk-alert>
            <bk-radio-group v-model="paramsType">
                <bk-radio :value="'default'">{{ $t('使用流程默认参数值') }}</bk-radio>
                <bk-radio :value="'reuse'">
                    {{ $t('重用当前任务参数值') }}
                    <bk-popover placement="bottom-end" theme="light" width="344" :ext-cls="'reuse-rule-tip'">
                        <i class="bk-icon icon-question-circle"></i>
                        <div slot="content">
                            <p class="mb10">{{ $t('以下情况参数值无法重用，使用变量默认值：') }}</p>
                            <p>{{ '1. ' + $t('变量的类型变更') }}</p>
                            <p>{{ '2. ' + $t('变量默认值的字段增减') }}</p>
                            <p>{{ '3. ' + $t('下拉框、表格类型变量的配置变更') }}</p>
                        </div>
                    </bk-popover>
                </bk-radio>
            </bk-radio-group>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    import TaskCreateDialog from './TaskCreateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import moment from 'moment-timezone'
    import TaskCloneDialog from './TaskCloneDialog.vue'
    import Skeleton from '@/components/skeleton/index.vue'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'
    const SEARCH_LIST = [
        {
            id: 'id',
            name: 'ID'
        },
        {
            id: 'taskName',
            name: i18n.t('任务名'),
            isDefaultOption: true
        },
        {
            id: 'creator',
            name: i18n.t('创建人')
        },
        {
            id: 'executor',
            name: i18n.t('执行人')
        },
        {
            id: 'statusSync',
            name: i18n.t('状态'),
            children: [
                { id: 'nonExecution', name: i18n.t('未执行') },
                { id: 'running', name: i18n.t('未完成') },
                { id: 'revoked', name: i18n.t('撤销') },
                { id: 'finished', name: i18n.t('完成') }
            ]
        },
        {
            id: 'create_method',
            name: i18n.t('创建方式'),
            children: []
        },
        {
            id: 'recorded_executor_proxy',
            name: i18n.t('执行代理人')
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
            width: 100
        },
        {
            id: 'name',
            label: i18n.t('任务名称'),
            disabled: true,
            min_width: 240
        },
        {
            id: 'start_time',
            label: i18n.t('执行开始'),
            width: 200
        },
        {
            id: 'finish_time',
            label: i18n.t('执行结束'),
            width: 200
        },
        {
            id: 'create_time',
            label: i18n.t('创建时间'),
            width: 200
        },
        {
            id: 'category_name',
            label: i18n.t('任务类型'),
            width: 100
        },
        {
            id: 'creator_name',
            label: i18n.t('创建人'),
            width: 120
        },
        {
            id: 'executor_name',
            label: i18n.t('执行人'),
            width: 120
        },
        {
            id: 'recorded_executor_proxy',
            label: i18n.t('执行代理人'),
            disabled: true,
            width: 120
        },
        {
            id: 'create_method',
            label: i18n.t('创建方式'),
            width: 100
        },
        {
            id: 'task_status',
            label: i18n.t('状态'),
            width: 120
        },
        {
            id: 'engine_ver',
            label: i18n.t('引擎版本'),
            width: 120
        }
    ]
    export default {
        name: 'TaskList',
        components: {
            Skeleton,
            NoData,
            TaskCreateDialog,
            TaskCloneDialog,
            SearchSelect
        },
        mixins: [permission, task],
        props: {
            project_id: {
                type: [String, Number],
                default: ''
            }
        },
        data () {
            const {
                page = 1,
                limit = 15,
                template_source = '',
                create_info = '',
                start_time = '',
                create_time = '',
                finish_time = '',
                creator = '',
                executor = '',
                statusSync = '',
                taskName = '',
                task_id = '',
                create_method = '',
                recorded_executor_proxy = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'start_time', name: i18n.t('执行时间'), type: 'dateRange' },
                { id: 'create_time', name: i18n.t('创建时间'), type: 'dateRange' },
                { id: 'finish_time', name: i18n.t('结束时间'), type: 'dateRange' }
            ]
            const searchSelectValue = searchList.reduce((acc, cur) => {
                const values_text = this.$route.query[cur.id]
                if (values_text) {
                    let values = []
                    if (!cur.children) {
                        values = cur.type === 'dateRange' ? values_text.split(',') : [values_text]
                        acc.push({ ...cur, values })
                    } else if (cur.children.length) {
                        const ids = values_text.split(',')
                        values = cur.children.filter(item => ids.includes(String(item.id)))
                        acc.push({ ...cur, values })
                    }
                }
                return acc
            }, [])
            return {
                firstLoading: true,
                listLoading: false,
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
                taskBasicInfoLoading: true,
                taskCreateMethodList: [],
                createInfo: create_info,
                templateSource: template_source,
                requestData: {
                    start_time: start_time ? start_time.split(',') : ['', ''],
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    finish_time: finish_time ? finish_time.split(',') : ['', ''],
                    creator,
                    executor,
                    statusSync,
                    taskName,
                    id: task_id,
                    create_method,
                    recorded_executor_proxy
                },
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                createMethodTabs: [
                    { id: 'all', name: i18n.t('全部') },
                    { id: 'app', name: i18n.t('手动任务') },
                    { id: 'api', name: 'API ' + i18n.t('任务') },
                    { id: 'periodic', name: i18n.t('周期任务') },
                    { id: 'clocked', name: i18n.t('计划任务') }
                ],
                crtCreateMethodTab: 'all', // 当前选中创建方法tab
                tableFields: TABLE_FIELDS,
                defaultSelected: ['id', 'name', 'start_time', 'finish_time', 'executor_name', 'task_status', 'recorded_executor_proxy'],
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                },
                isCreateDialogShow: false,
                paramsType: 'default',
                selectedRow: {},
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue,
                isInitCreateMethod: false
            }
        },
        computed: {
            ...mapState({
                taskList: state => state.taskList.taskListData
            }),
            ...mapState('project', {
                'authActions': state => state.authActions,
                'timeZone': state => state.timezone
            })
        },
        async created () {
            this.getFields()
            await this.getData()
            this.firstLoading = false
        },
        methods: {
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'getTaskHasSubTaskList',
                'getTaskHasSubTasks'
            ]),
            ...mapActions('task/', [
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
                    const { start_time, create_time, finish_time, creator, executor, statusSync, taskName, id, create_method, recorded_executor_proxy } = this.requestData
                    let pipeline_instance__is_started
                    let pipeline_instance__is_finished
                    let pipeline_instance__is_revoked
                    switch (statusSync) {
                        case 'nonExecution':
                            pipeline_instance__is_started = false
                            break
                        case 'running':
                            pipeline_instance__is_started = true
                            pipeline_instance__is_finished = false
                            pipeline_instance__is_revoked = false
                            break
                        case 'revoked':
                            pipeline_instance__is_revoked = true
                            break
                        case 'finished':
                            pipeline_instance__is_finished = true
                            break
                    }

                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        template_id: this.templateId || undefined,
                        pipeline_instance__creator__contains: creator || undefined,
                        pipeline_instance__executor__contains: executor || undefined,
                        pipeline_instance__name__icontains: taskName || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        pipeline_instance__is_revoked,
                        create_info: this.createInfo || undefined,
                        project__id: this.project_id,
                        template_source: this.templateSource || undefined,
                        id: id || undefined,
                        create_method: create_method || undefined,
                        recorded_executor_proxy: recorded_executor_proxy || undefined
                    }

                    if (start_time && start_time[0] && start_time[1]) {
                        if (this.template_source === 'common') {
                            data['pipeline_template__start_time__gte'] = moment(start_time[0]).format('YYYY-MM-DD')
                            data['pipeline_template__start_time__lte'] = moment(start_time[1]).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['pipeline_instance__start_time__gte'] = moment.tz(start_time[0], this.timeZone).format('YYYY-MM-DD')
                            data['pipeline_instance__start_time__lte'] = moment.tz(start_time[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    if (create_time && create_time[0] && create_time[1]) {
                        if (this.template_source === 'common') {
                            data['pipeline_template__create_time__gte'] = moment(create_time[0]).format('YYYY-MM-DD')
                            data['pipeline_template__create_time__lte'] = moment(create_time[1]).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['pipeline_instance__create_time__gte'] = moment.tz(create_time[0], this.timeZone).format('YYYY-MM-DD')
                            data['pipeline_instance__create_time__lte'] = moment.tz(create_time[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    if (finish_time && finish_time[0] && finish_time[1]) {
                        if (this.template_source === 'common') {
                            data['pipeline_template__finish_time__gte'] = moment(finish_time[0]).format('YYYY-MM-DD')
                            data['pipeline_template__finish_time__lte'] = moment(finish_time[1]).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['pipeline_instance__finish_time_gte'] = moment.tz(finish_time[0], this.timeZone).format('YYYY-MM-DD')
                            data['pipeline_instance__finish_time__lte'] = moment.tz(finish_time[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    const taskListData = await this.loadTaskList(data)
                    const list = taskListData.results
                    // 设置level初始值
                    list.forEach(item => {
                        item.level = 1
                    })
                    this.pagination.count = taskListData.count
                    this.totalCount = taskListData.count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                    const result = await this.setListHaveChild(list)
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', result)
                    this.setTaskListData(result)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            // 设置每条记录是否有子流程
            async setListHaveChild (list) {
                const ids = list.map(item => item.id)
                const checkStatus = await this.getTaskHasSubTasks({
                    project_id: this.project_id,
                    task_ids: ids.toString()
                })
                list.forEach(item => {
                    item.isHasChild = checkStatus.data.has_children_taskflow[item.id]
                })
                return list
            },
            // 获取当前流程的子流程列表
            async getCurProcessChdProcess (row) {
                const curTaskList = toolsUtils.deepClone(this.$store.state.taskList.taskListData)
                const curParent = curTaskList.find(item => item.id === row.id)
                curParent.isOpen = !row.isOpen
                // table field
                const curField = this.setting.fieldList.find(item => item.id)
                if (curParent.isOpen && row.level) {
                    const params = {
                        root_task_id: row.id,
                        project_id: this.project_id
                    }
                    const res = await this.getTaskHasSubTaskList(params)
                    const { tasks, relations } = res.data
                    for (const key in relations) {
                        if (row.id === Number(key)) {
                            relations[key].forEach(id => {
                                const task = tasks.find(item => item.id === id)
                                task.level = row.level + 1
                                task.parent_id = row.id
                                curTaskList.splice(curTaskList.findIndex(item => item.id === row.id) + 1, 0, task)
                            })
                        }
                    }
                    const result = await this.setListHaveChild(curTaskList)
                    this.getExecuteStatus('executeStatus', result)
                    this.setTaskListData(result)
                    curField.width = 30 * (curParent.level) + 100
                } else {
                    const filterArr = this.filterTaskList(curTaskList, curParent.id)
                    this.getExecuteStatus('executeStatus', filterArr)
                    this.setTaskListData(filterArr)
                    curField.width = 30 * (curParent.level - 1) + 100
                }
            },
            // 关闭展开icon过滤列表
            filterTaskList (list, id, ids = []) {
                list.map(item => {
                    if (item.parent_id === id) {
                        ids.push(item.id)
                        this.filterTaskList(list, item.id, ids)
                    }
                })
                return list.filter(item => !ids.includes(item.id))
            },
            async getBizBaseInfo () {
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.taskCategory = res.data.task_categories
                    this.setProjectBaseInfo(res.data)
                    this.taskBasicInfoLoading = false
                } catch (e) {
                    console.log(e)
                }
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('TaskList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.defaultSelected
                    if (!fieldList || !size) {
                        localStorage.removeItem('TaskList')
                    }
                } else {
                    selectedFields = this.defaultSelected
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
            },
            // 创建方式tab切换
            handleCreateMethodTabClick (method) {
                this.crtCreateMethodTab = method
                const index = this.searchSelectValue.findIndex(item => item.id === 'create_method')
                const form = this.searchList.find(item => item.id === 'create_method')
                const values = form.children.filter(item => item.id === method)
                if (method === 'all' && index > -1) {
                    this.searchSelectValue.splice(index, 1)
                } else if (method !== 'all') {
                    const methodInfo = this.searchSelectValue[index]
                    if (methodInfo) {
                        methodInfo.values = values
                    } else {
                        this.searchSelectValue.push({ ...form, values })
                    }
                }
            },
            hasCreateTaskPerm (task) {
                const authActions = [...task.auth_actions, ...this.authActions]
                const reqPerm = task.template_source === 'project' ? 'flow_create_task' : 'common_flow_create_task'
                return this.hasPermission([reqPerm], authActions)
            },
            getCreateTaskUrl (task) {
                this.selectedRow = task
                this.isCreateDialogShow = true
            },
            onCreateConfirm () {
                const { id, template_id, template_source } = this.selectedRow
                const taskId = this.paramsType === 'reuse' ? id : undefined
                const url = {
                    name: 'taskCreate',
                    query: { template_id: template_id, task_id: taskId },
                    params: { project_id: this.project_id, step: 'selectnode' }
                }
                if (template_source === 'common') {
                    url.query.common = 1
                }
                this.isCreateDialogShow = false
                this.$router.push(url)
            },
            /**
             * 单个任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} task 任务数据对象
             */
            onTaskPermissonCheck (required, task) {
                const resourceData = {
                    task: [{
                        id: task.id,
                        name: task.name
                    }],
                    project: [{
                        id: task.project.id,
                        name: task.project.name
                    }]
                }
                const flowKey = task.template_source === 'project' ? 'flow' : 'common_flow'
                resourceData[flowKey] = [{
                    id: task.template_id,
                    name: task.template_name
                }]
                this.applyForPermission(required, [...task.auth_actions, ...this.authActions], resourceData)
            },
            onDeleteTask (task) {
                if (!this.hasPermission(['task_delete'], task.auth_actions)) {
                    this.onTaskPermissonCheck(['task_delete'], task)
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
                    this.$bkMessage({
                        message: i18n.t('任务') + i18n.t('删除成功！'),
                        theme: 'success'
                    })
                } catch (e) {
                    console.log(e)
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
            onCloneTaskClick (task) {
                if (!this.hasPermission(['task_clone'], task.auth_actions)) {
                    this.onTaskPermissonCheck(['task_clone'], task)
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
                    console.log(e)
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
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('TaskList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property === 'recorded_executor_proxy') {
                    return h('span', {
                        'class': 'recorded_executor_proxy-label'
                    }, [
                        column.label,
                        h('i', {
                            'class': 'common-icon-info table-header-tips',
                            directives: [{
                                name: 'bk-tooltips',
                                value: i18n.t('执行代理人在任务开始执行时确定，未执行任务不展示')
                            }]
                        })
                    ])
                } else if (['start_time', 'create_time', 'finish_time'].includes(column.property)) {
                    const id = this.setting.selectedFields[$index].id
                    const date = this.requestData[id]
                    return <TableRenderHeader
                        name={ column.label }
                        orderShow = { false }
                        dateValue={ date }
                        onDateChange={ data => this.handleDateTimeFilter(data, id) }>
                    </TableRenderHeader>
                } else {
                    return column.label
                }
            },
            handleDateTimeFilter (date = [], id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                if (date.length) {
                    if (index > -1) {
                        this.searchSelectValue[index].values = date
                    } else {
                        const info = {
                            id,
                            type: 'dateRange',
                            name: id === 'start_time' ? i18n.t('执行时间') : id === 'create_time' ? i18n.t('创建时间') : i18n.t('结束时间'),
                            values: date
                        }
                        this.searchSelectValue.push(info)
                        // 添加搜索记录
                        const searchDom = this.$refs.searchSelect
                        searchDom && searchDom.addSearchRecord(info)
                    }
                } else if (index > -1) {
                    this.searchSelectValue.splice(index, 1)
                }
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getTaskList()
            },
            onPageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getTaskList()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { start_time, create_time, finish_time, creator, executor, statusSync, taskName, id, create_method, recorded_executor_proxy } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    executor,
                    statusSync,
                    page: current,
                    start_time: start_time && start_time.every(item => item) ? start_time.join(',') : '',
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    finish_time: finish_time && finish_time.every(item => item) ? finish_time.join(',') : '',
                    taskName,
                    task_id: id,
                    create_method,
                    recorded_executor_proxy
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.replace({ name: 'taskList', params: { project_id: this.project_id }, query })
            },
            async getCreateMethod () {
                try {
                    const createMethodData = await this.loadCreateMethod()
                    this.taskCreateMethodList = createMethodData.data.map(m => ({ value: m.value, name: m.name }))
                    const form = this.searchList.find(item => item.id === 'create_method')
                    form.children = this.taskCreateMethodList.map(item => {
                        return { id: item.value, name: item.name }
                    })
                    // 因为任务类型列表是通过接口获取的，所以需要把路径上的类型添加进去
                    const id = this.$route.query['create_method']
                    if (id) {
                        const match = this.createMethodTabs.some(item => item.id === id)
                        if (match) {
                            this.crtCreateMethodTab = id
                        }
                        this.isInitCreateMethod = true
                        const values = form.children.filter(item => id === item.id)
                        this.searchSelectValue.push({ ...form, values })
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getData () {
                Promise.all([
                    this.getTaskList(),
                    this.getCreateMethod(),
                    this.getBizBaseInfo()
                ]).catch(e => {
                    console.log(e)
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
            handleSearchValueChange (data) {
                data = data.reduce((acc, cur) => {
                    if (cur.type === 'dateRange') {
                        acc[cur.id] = cur.values
                    } else if (cur.multiable) {
                        acc[cur.id] = cur.values.map(item => item.id)
                    } else {
                        const value = cur.values[0]
                        acc[cur.id] = cur.children ? value.id : value
                    }
                    return acc
                }, {})
                const method = data['create_method']
                if (method) {
                    const match = this.createMethodTabs.some(item => item.id === method)
                    if (match) {
                        this.crtCreateMethodTab = method
                    }
                } else {
                    this.crtCreateMethodTab = 'all'
                }
                this.requestData = data
                this.pagination.current = 1
                // 当拉取创建方式列表时，不需要更新任务列表
                if (this.isInitCreateMethod) {
                    this.isInitCreateMethod = false
                    return
                }
                // 搜索时，清空 createInfo、templateId、templateSource 筛选条件
                this.createInfo = ''
                this.templateId = ''
                this.templateSource = ''
                this.updateUrl()
                this.getTaskList()
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/advancedSearch.scss';
@import '@/scss/task.scss';
@import '@/scss/mixins/scrollbar.scss';
@include advancedSearch;

.show-chd {
    transform: rotate(90deg);
    display: inline-block;
    transition: 0.5s;
}
.close-chd {
    transform: rotate(0deg);
    display: inline-block;
    transition: 0.5s;
}
.task-container {
    height: 100%;
}
.task-create-method-tabs {
    position: relative;
    display: flex;
    align-items: center;
    padding: 0 24px;
    background: #ffffff;
    box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    z-index: 101;
}
.create-method-tab-item {
    margin-right: 17px;
    padding: 0 7px;
    height: 36px;
    line-height: 36px;
    font-size: 14px;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    &.active {
        color: #3a84ff;
        border-bottom: 2px solid #3a84ff;
    }
}
.task-content-wrapper {
    padding: 20px 24px;
    height: calc(100% - 36px);
    overflow: auto;
    @include scrollbar;
}
.search-wrapper {
    position: relative;
    display: flex;
    justify-content: space-between;
}
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
        .task-operation-btn {
            padding: 5px;
            color: #3a84ff;
            font-size: 12px;
            cursor: pointer;
            &.disabled {
                color: #cccccc;
                cursor: not-allowed;
            }
        }
    }
    .empty-data {
        padding: 120px 0;
    }
    .template-operate-btn {
        color: $blueDefault;
    }
    /deep/.table-header-tips {
        margin-left: 4px;
        font-size: 14px;
        color: #c4c6cc;
        cursor: pointer;
    }
}
</style>
<style lang="scss">
    .recreate-dialog {
        .bk-dialog-header {
            padding-bottom: 10px;
        }
        .bk-alert {
            margin-bottom: 26px;
        }
        .bk-form-control {
            display: flex;
            justify-content: space-between;
            padding: 0 24px;
            .bk-form-radio {
                font-size: 12px;
                .icon-question-circle {
                    font-size: 14px;
                }
            }

        }
    }
</style>
