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
                        <search-select
                            ref="searchSelect"
                            id="taskList"
                            :placeholder="$t('ID/任务名/创建人/执行人/状态/执行方式/执行代理人')"
                            v-model="searchSelectValue"
                            :search-list="searchList"
                            @change="handleSearchValueChange">
                        </search-select>
                    </div>
                    <div class="task-table-content" data-test-id="taskList_table_taskList">
                        <bk-table
                            ref="templateTable"
                            :data="taskList"
                            :size="setting.size"
                            :row-class-name="getRowClassName"
                            v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: !firstLoading && taskList.length ? 0.6 : 1, zIndex: 100 }"
                            @row-click="selectedTaskId = ''">
                            <bk-table-column
                                v-for="item in setting.selectedFields"
                                :key="item.id"
                                :label="item.label"
                                :label-class-name="item.id === 'id' ? 'task-id' : ''"
                                :prop="item.id"
                                :render-header="renderTableHeader"
                                :width="item.width"
                                show-overflow-tooltip
                                :min-width="item.min_width">
                                <template slot-scope="props">
                                    <!--任务名称-->
                                    <div v-if="item.id === 'id'">
                                        <span v-if="props.row.isHasChild || (props.row.children && props.row.children.length !== 0)" :style="{ 'margin-left': `${(props.row.level) * 20}px` }">
                                            <i
                                                :class="['commonicon-icon', 'common-icon-next-triangle-shape', props.row.isOpen ? 'show-chd' : 'close-chd']"
                                                @click="getCurProcessChdProcess(props.row)">
                                            </i>
                                        </span>
                                        <span v-else :style="{ 'margin-left': `${(props.row.level) * 20}px`, width: '12px', display: 'inline-block' }"></span>
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
                                                query: { instance_id: props.row.id, root_id: props.row.root_id }
                                            }">
                                            {{props.row.name}}
                                        </router-link>
                                    </div>
                                    <!--执行方式-->
                                    <div v-else-if="item.id === 'create_method'">
                                        {{ transformCreateMethod(props.row.create_method) }}
                                    </div>
                                    <!--状态-->
                                    <div v-else-if="item.id === 'task_status'" class="task-status">
                                        <span :class="executeStatus[props.row.id] && executeStatus[props.row.id].cls"></span>
                                        <span v-if="executeStatus[props.row.id]" class="task-status-text">{{executeStatus[props.row.id].text}}</span>
                                    </div>
                                    <!--任务类型-->
                                    <div v-else-if="item.id === 'flow_type'">
                                        {{ props.row.flow_type === 'common_func' ? $t('task_职能化') : $t('常规') }}
                                    </div>
                                    <!-- 其他 -->
                                    <template v-else>
                                        <span :title="props.row[item.id] || '--'">{{ props.row[item.id] || '--' }}</span>
                                    </template>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('操作')" width="150" :fixed="taskList.length ? 'right' : false">
                                <template slot-scope="props">
                                    <div v-if="props.row.is_child_taskflow" class="task-operation">
                                        <span class="default">{{ '--' }}</span>
                                        <span>{{ '--' }}</span>
                                    </div>
                                    <div v-else class="task-operation" :task-name="props.row.name">
                                        <!-- 事后鉴权，后续对接新版权限中心 -->
                                        <a v-if="props.row.template_deleted || props.row.template_source === 'onetime'" class="task-operation-btn disabled" data-test-id="taskList_table_reexecuteBtn">{{$t('重新执行')}}</a>
                                        <a
                                            v-else-if="!hasCreateTaskPerm(props.row)"
                                            v-cursor
                                            class="text-permission-disable task-operation-btn"
                                            data-test-id="taskList_table_reexecuteBtn"
                                            @click="onTaskPermissonCheck([props.row.template_source === 'project' ? 'flow_create_task' : 'common_flow_create_task'], props.row)">
                                            {{$t('重新执行')}}
                                        </a>
                                        <a
                                            v-else
                                            v-bk-tooltips.top="$t('复⽤参数值并使⽤流程最新数据重新执行')"
                                            class="task-operation-btn"
                                            data-test-id="taskList_table_reexecuteBtn"
                                            @click="getCreateTaskUrl(props.row)">
                                            {{$t('重新执行')}}
                                        </a>
                                        <a
                                            v-if="executeStatus[props.row.id] && executeStatus[props.row.id].text === $t('未执行')"
                                            v-cursor="{ active: !hasPermission(['task_delete'], props.row.auth_actions) }"
                                            :class="['task-operation-btn', {
                                                'text-permission-disable': !hasPermission(['task_delete'], props.row.auth_actions)
                                            }]"
                                            href="javascript:void(0);"
                                            data-test-id="taskList_table_deleteBtn"
                                            @click="onDeleteTask(props.row, $event)">
                                            {{ $t('删除') }}
                                        </a>
                                        <a
                                            v-else
                                            v-bk-tooltips.top="$t('仅“未执行”的任务才可删除')"
                                            class="task-operation-btn disabled"
                                            data-test-id="taskList_table_deleteBtn">
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
                            <div class="empty-data" slot="empty">
                                <NoData
                                    :type="searchSelectValue.length ? 'search-empty' : 'empty'"
                                    :message="searchSelectValue.length ? $t('搜索结果为空') : ''"
                                    @searchClear="searchSelectValue = []">
                                </NoData>
                            </div>
                        </bk-table>
                        <div
                            v-if="countLoading || listLoading || pagination.count"
                            class="bk-table-pagination-wrapper"
                            v-bkloading="{ isLoading: countLoading || listLoading, zIndex: 100 }">
                            <bk-pagination
                                size="small"
                                v-bind="pagination"
                                :location="'left'"
                                :align="'right'"
                                :show-limit="true"
                                :show-total-count="true"
                                @change="onPageChange"
                                @limit-change="onPageLimitChange">
                            </bk-pagination>
                        </div>
                    </div>
                </div>
            </skeleton>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import moment from 'moment-timezone'
    import Skeleton from '@/components/skeleton/index.vue'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'
    import CancelRequest from '@/api/cancelRequest.js'

    const TASK_STATUS_LIST = [
        { id: 'nonExecution', name: i18n.t('未执行') },
        { id: 'running', name: i18n.t('未完成') },
        // { id: 'failed', name: i18n.t('失败') },
        // { id: 'pause', name: i18n.t('暂停') },
        { id: 'finished', name: i18n.t('完成') },
        { id: 'revoked', name: i18n.t('终止') }
    ]

    const SEARCH_LIST = [
        {
            id: 'task_id',
            name: 'ID'
        },
        {
            id: 'taskName',
            name: i18n.t('task_任务名'),
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
            children: TASK_STATUS_LIST
        },
        {
            id: 'create_method',
            name: i18n.t('执行方式'),
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
            width: 120
        },
        {
            id: 'name',
            label: i18n.t('task_任务名称'),
            disabled: true,
            min_width: 240
        },
        {
            id: 'task_status',
            label: i18n.t('状态'),
            disabled: true,
            width: 120
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
            label: i18n.t('执行方式'),
            width: 100
        },
        {
            id: 'flow_type',
            label: i18n.t('task_任务类型'),
            width: 100
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
            const dateInfo = { start_time, create_time, finish_time }
            const searchList = [
                ...SEARCH_LIST,
                { id: 'start_time', name: i18n.t('执行开始'), type: 'dateRange' },
                { id: 'create_time', name: i18n.t('创建时间'), type: 'dateRange' },
                { id: 'finish_time', name: i18n.t('执行结束'), type: 'dateRange' }
            ]
            const searchSelectValue = searchList.reduce((acc, cur) => {
                const values_text = this.$route.query[cur.id]
                if (values_text) {
                    let values = []
                    if (!cur.children) {
                        if (cur.type === 'dateRange') {
                            // 判断时间是否超出
                            const startDate = values_text.split(',')[0]
                            const isExceed = this.judgeDateIsExceed(startDate)
                            if (isExceed) {
                                dateInfo[cur.id] = ''
                            } else {
                                values = values_text.split(',')
                                acc.push({ ...cur, values })
                            }
                        } else {
                            values = [values_text]
                            acc.push({ ...cur, values })
                        }
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
                countLoading: false,
                templateId: this.$route.query.template_id,
                searchStr: '',
                executeStatus: {}, // 任务执行状态
                totalPage: 1,
                shapeShow: false,
                businessInfoLoading: true, // 模板分类信息 loading
                taskBasicInfoLoading: true,
                taskCreateMethodList: [],
                createInfo: create_info,
                templateSource: template_source,
                requestData: {
                    start_time: dateInfo.start_time ? dateInfo.start_time.split(',') : ['', ''],
                    create_time: dateInfo.create_time ? dateInfo.create_time.split(',') : ['', ''],
                    finish_time: dateInfo.finish_time ? dateInfo.finish_time.split(',') : ['', ''],
                    creator,
                    executor,
                    statusSync,
                    taskName,
                    task_id,
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
                    { id: 'api', name: i18n.t('API 任务') },
                    { id: 'periodic', name: i18n.t('task_周期任务') },
                    { id: 'clocked', name: i18n.t('task_计划任务') }
                ],
                crtCreateMethodTab: 'all', // 当前选中创建方法tab
                tableFields: TABLE_FIELDS,
                defaultSelected: ['id', 'name', 'start_time', 'finish_time', 'executor_name', 'task_status', 'recorded_executor_proxy'],
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                },
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue,
                isInitCreateMethod: false,
                deletaLoading: false,
                initOpenTask: [],
                selectedTaskId: '',
                tableMaxHeight: window.innerHeight - 180 - 63 // 63为分页高度
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
            const { root_id, task_id } = this.$route.params
            this.initOpenTask = root_id ? String(root_id).split(',') : []
            this.selectedTaskId = task_id || ''
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
                'loadTaskCount'
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
                this.executeStatus = {}
                try {
                    const params = this.getQuery()
                    params.without_count = true
                    const source = new CancelRequest()
                    const taskListData = await this.loadTaskList({
                        params,
                        config: { cancelToken: source.token }
                    })
                    const list = taskListData.results
                    // 设置level初始值
                    list.forEach(item => {
                        item.level = 0
                    })

                    const result = await this.setListHaveChild(list)
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', result)
                    this.setTaskListData(result)
                    // 当存在默认打开的子流程时，需手动打开
                    if (this.initOpenTask.length) {
                        const task = result.find(item => item.id === Number(this.initOpenTask[0]))
                        task && await this.getCurProcessChdProcess(task)
                        this.initOpenTask = []
                        return
                    }
                } catch (e) {
                    this.listLoading = e.message === 'cancelled'
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            async getTaskCount () {
                this.countLoading = true
                try {
                    const params = this.getQuery()
                    const source = new CancelRequest('task-count')
                    const resp = await this.loadTaskCount({
                        params,
                        config: { cancelToken: source.token }
                    })
                    this.pagination.count = resp.count
                    this.totalCount = resp.count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (error) {
                    this.countLoading = error.message === 'cancelled'
                    console.warn(error)
                } finally {
                    this.countLoading = false
                }
            },
            getQuery () {
                const { start_time, create_time, finish_time, creator, executor, statusSync, taskName, task_id, create_method, recorded_executor_proxy } = this.requestData
                let pipeline_instance__is_started
                let pipeline_instance__is_finished
                let pipeline_instance__is_revoked
                let task_instance_status
                switch (statusSync) {
                    case 'nonExecution':
                        pipeline_instance__is_started = false
                        break
                    // case 'failed':
                    // case 'pause':
                    case 'running':
                        pipeline_instance__is_started = true
                        pipeline_instance__is_finished = false
                        pipeline_instance__is_revoked = false
                        // task_instance_status = statusSync
                        break
                    case 'revoked':
                        pipeline_instance__is_revoked = true
                        break
                    case 'finished':
                        pipeline_instance__is_finished = true
                        break
                    case 'pending_processing':
                        pipeline_instance__is_started = true
                        pipeline_instance__is_finished = false
                        pipeline_instance__is_revoked = false
                        task_instance_status = 'pending_processing'
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
                    id: task_id || undefined,
                    create_method: create_method || undefined,
                    recorded_executor_proxy: recorded_executor_proxy || undefined,
                    is_child_taskflow: false,
                    task_instance_status: task_instance_status || undefined
                }

                if (start_time && start_time[0] && start_time[1]) {
                    if (this.template_source === 'common') {
                        data['pipeline_template__start_time__gte'] = moment(start_time[0]).format('YYYY-MM-DD HH:mm:ss')
                        data['pipeline_template__start_time__lte'] = moment(start_time[1]).format('YYYY-MM-DD HH:mm:ss')
                    } else {
                        data['pipeline_instance__start_time__gte'] = moment.tz(start_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        data['pipeline_instance__start_time__lte'] = moment.tz(start_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    }
                }
                if (create_time && create_time[0] && create_time[1]) {
                    if (this.template_source === 'common') {
                        data['pipeline_template__create_time__gte'] = moment(create_time[0]).format('YYYY-MM-DD HH:mm:ss')
                        data['pipeline_template__create_time__lte'] = moment(create_time[1]).format('YYYY-MM-DD HH:mm:ss')
                    } else {
                        data['pipeline_instance__create_time__gte'] = moment.tz(create_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        data['pipeline_instance__create_time__lte'] = moment.tz(create_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    }
                }
                if (finish_time && finish_time[0] && finish_time[1]) {
                    if (this.template_source === 'common') {
                        data['pipeline_template__finish_time__gte'] = moment(finish_time[0]).format('YYYY-MM-DD HH:mm:ss')
                        data['pipeline_template__finish_time__lte'] = moment(finish_time[1]).format('YYYY-MM-DD HH:mm:ss')
                    } else {
                        data['pipeline_instance__finish_time__gte'] = moment.tz(finish_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        data['pipeline_instance__finish_time__lte'] = moment.tz(finish_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    }
                }
                return data
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
                curParent.maxLevel = ''
                // table field
                const curField = this.setting.fieldList.find(item => item.id)
                let result = []
                if (curParent.isOpen) {
                    // 处理task与relations
                    const taskIds = [] // task id
                    const taskIdList = []
                    if (curParent.children && curParent.children.length !== 0) {
                        curParent.children.forEach(item => {
                            item.isOpen = false // 子流程默认icon close
                            item.level = curParent.level + 1
                            result.push(item)
                        })
                        curField.width = 20 * (curParent.level + 1) + 100
                    } else {
                        const params = {
                            root_task_id: row.id,
                            project_id: this.project_id
                        }
                        const res = await this.getTaskHasSubTaskList(params)
                        const { tasks, relations } = res.data
                        for (const key in relations) {
                            taskIds.push({
                                id: Number(key),
                                children_id: [...relations[key]]
                            })
                        }
                        const rootObj = {}
                        taskIds.forEach(item => {
                            item.children_id.forEach(ite => {
                                rootObj[ite] = item.id in rootObj ? rootObj[item.id] + ',' + item.id : item.id
                                taskIdList.push({
                                    id: ite,
                                    parent_id: item.id,
                                    root_id: rootObj[ite],
                                    children: []
                                })
                            })
                        })
                        const arrToTree = (arr, parentId, level = 1) => {
                            const result = []
                            curParent.maxLevel = level
                            arr.forEach(item => {
                                if (item.parent_id === parentId) {
                                    const task = tasks.find(task => task.id === item.id)
                                    task.root_id = item.root_id
                                    result.push({
                                        ...item,
                                        level: level,
                                        ...task,
                                        children: arrToTree(arr, item.id, level + 1)
                                    })
                                }
                            })
                            return result
                        }
                        result = arrToTree(taskIdList, Number(row.id))
                        curField.width = 20 * curParent.maxLevel + 100
                    }
                    curTaskList.splice(curTaskList.findIndex(item => item.id === row.id) + 1, 0, ...result)
                    this.getExecuteStatus('executeStatus', [...result, row])
                    this.setTaskListData(curTaskList)
                    // 当存在默认打开的子流程时，需手动打开
                    if (this.initOpenTask.length) {
                        result.forEach(task => {
                            if (this.initOpenTask.includes(String(task.id))) {
                                this.getCurProcessChdProcess(task)
                            }
                        })
                    }
                } else {
                    // 关闭获取已展开列的最大level
                    const MaxLevel = Math.max(...curTaskList.map(item => {
                        if (item.isOpen) {
                            return item.maxLevel
                        } else {
                            return 0
                        }
                    }))
                    const filterArr = this.filterTaskList(curTaskList, curParent.id)
                    this.getExecuteStatus('executeStatus', [row])
                    this.setTaskListData(filterArr)
                    curField.width = 20 * MaxLevel + 100
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
                const { id, template_id, template_source } = task
                const url = {
                    name: 'taskCreate',
                    query: { template_id: template_id, task_id: id, entrance: 'taskflow' },
                    params: { project_id: this.project_id, step: 'selectnode' }
                }
                if (template_source === 'common') {
                    url.query.common = 1
                }
                this.$router.push(url)
            },
            onDeleteTask (task) {
                if (!this.hasPermission(['task_delete'], task.auth_actions)) {
                    this.onTaskPermissonCheck(['task_delete'], task)
                    return
                }
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除') + i18n.t('任务') + '"' + task.name + '"?'])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.onDeleteConfirm(task.id)
                    }
                })
            },
            async onDeleteConfirm (taskId) {
                if (this.deletaLoading) return
                this.deletaLoading = true
                try {
                    const resp = await this.deleteTask(taskId)
                    if (resp.result === false) return
                    // 最后一页最后一条删除后，往前翻一页
                    if (
                        this.pagination.current > 1
                        && this.totalPage === this.pagination.current
                        && this.pagination.count - (this.totalPage - 1) * this.pagination.limit === 1
                    ) {
                        this.pagination.current -= 1
                    }
                    this.getTaskList()
                    this.getTaskCount()
                    this.$bkMessage({
                        message: i18n.t('任务') + i18n.t('删除成功！'),
                        theme: 'success'
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.deletaLoading = false
                }
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
                        h('p', {
                            'class': 'label-text',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [column.label]),
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
                } else if (column.property === 'task_status') {
                    const data = this.searchSelectValue.find(item => item.id === 'statusSync')
                    const filterConfig = {
                        show: true,
                        list: TASK_STATUS_LIST,
                        values: data ? data.values : [],
                        multiple: false,
                        extCls: 'task-status-popover'
                    }
                    return <TableRenderHeader
                        name={ column.label }
                        property={ column.property }
                        orderShow={ false }
                        dateFilterShow={ false }
                        filterConfig = { filterConfig }
                        onFilterChange={ data => this.handleTaskStatusFilter(data) }>
                    </TableRenderHeader>
                } else {
                    return h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        column.label
                    ])
                }
            },
            handleTaskStatusFilter (data) {
                const index = this.searchSelectValue.findIndex(item => item.id === 'statusSync')
                if (data.length) {
                    if (index > -1) {
                        this.searchSelectValue[index].values = data
                    } else {
                        const form = this.searchList.find(item => item.id === 'statusSync')
                        this.searchSelectValue.push({ ...form, values: data })
                    }
                } else if (index > -1) {
                    this.searchSelectValue.splice(index, 1)
                }
            },
            handleDateTimeFilter (date = [], id) {
                // 判断时间是否超出
                const isExceed = this.judgeDateIsExceed(date[0])
                if (isExceed) return
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                if (date.length) {
                    if (index > -1) {
                        this.searchSelectValue[index].values = date
                    } else {
                        const info = {
                            id,
                            type: 'dateRange',
                            name: id === 'start_time' ? i18n.t('执行开始') : id === 'create_time' ? i18n.t('创建时间') : i18n.t('执行结束'),
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
            // 判断时间是否超出
            judgeDateIsExceed (date) {
                const oneDay = 24 * 60 * 60 * 1000
                const startDate = new Date(date).getTime()
                const nowDate = new Date().getTime()
                const diffTime = Math.abs(nowDate - startDate)
                const diffDays = Math.floor(diffTime / oneDay)
                if (diffDays > window.TASK_LIST_STATUS_FILTER_DAYS) {
                    this.$bkMessage({
                        message: i18n.t('仅支持查询最近x天任务记录', { x: window.TASK_LIST_STATUS_FILTER_DAYS }),
                        theme: 'warning'
                    })
                    return true
                }
                return false
            },
            getRowClassName ({ row }) {
                return this.selectedTaskId === row.id ? 'selected-row' : row.is_child_taskflow ? 'expand-row' : ''
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getTaskList()
                this.getTaskCount()
            },
            onPageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getTaskList()
                this.getTaskCount()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { start_time, create_time, finish_time, creator, executor, statusSync, taskName, task_id, create_method, recorded_executor_proxy } = this.requestData
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
                    task_id,
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
                    this.getTaskCount(),
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
            handleSearchValueChange (data) {
                data = data.reduce((acc, cur) => {
                    if (cur.type === 'dateRange') {
                        acc[cur.id] = cur.values
                    } else if (cur.multiable) {
                        acc[cur.id] = cur.values.map(item => item.id)
                    } else {
                        const value = cur.values[0]
                        acc[cur.id] = cur.children ? value.id : value?.replace(/\u00A0/g, ' ')
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
                this.getTaskCount()
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
    position: relative;
    top: -2px;
    cursor: pointer;
}
.close-chd {
    transform: rotate(0deg);
    display: inline-block;
    transition: 0.5s;
    position: relative;
    top: -1px;
    cursor: pointer;
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
    height: 32px;
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
        .default {
            padding-left: 7px;
            margin-right: 47px;
        }
    }
    ::v-deep .selected-row {
        background: #f0f5ff;
    }
    ::v-deep .expand-row {
        background: #fafbfd;
    }
    .template-operate-btn {
        color: $blueDefault;
    }
    ::v-deep .recorded_executor_proxy-label {
        display: flex;
        align-items: center;
        .table-header-tips {
            flex-shrink: 0;
            margin-left: 4px;
            font-size: 14px;
            color: #c4c6cc;
        }
    }
    ::v-deep .cell .task-id {
        margin-left: 16px;
    }
}
.bk-table-pagination-wrapper {
    height: 64px;
    border: 1px solid #dfe0e5;
}
</style>
<style lang="scss">
.task-status-popover {
    .option-list {
        width: 100px;
    }
}
</style>
