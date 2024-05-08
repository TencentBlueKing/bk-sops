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
    <div class="appmaker-container">
        <skeleton :loading="firstLoading" loader="commonList">
            <div class="list-wrapper">
                <div class="search-wrapper mb20">
                    <search-select
                        ref="searchSelect"
                        id="appMarkerTaskList"
                        :placeholder="$t('ID/任务名/执行人/状态')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="appmaker-table-content" data-test-id="appTaskHome_table_appmakerList">
                    <bk-table
                        :data="appmakerList"
                        :pagination="pagination"
                        v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }"
                        @page-change="onPageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column
                            v-for="item in tableFields"
                            :key="item.id"
                            :label="item.label"
                            :label-class-name="item.id === 'id' ? 'task-id' : ''"
                            :prop="item.id"
                            :render-header="renderTableHeader"
                            :width="item.width"
                            show-overflow-tooltip
                            :min-width="item.min_width">
                            <template slot-scope="props">
                                <!-- 任务ID -->
                                <template v-if="item.id === 'id'">
                                    <span v-if="props.row.isHasChild || (props.row.children && props.row.children.length !== 0)" :style="{ 'margin-left': `${(props.row.level) * 20}px` }">
                                        <i
                                            :class="['commonicon-icon', 'common-icon-next-triangle-shape', props.row.isOpen ? 'show-chd' : 'close-chd']"
                                            @click="getCurProcessChdProcess(props.row)">
                                        </i>
                                    </span>
                                    <span v-else :style="{ 'margin-left': `${(props.row.level) * 20}px`, width: '12px', display: 'inline-block' }"></span>
                                    <span>{{ props.row[item.id] || '--' }}</span>
                                </template>
                                <!-- 任务名 -->
                                <template v-else-if="item.id === 'name'">
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
                                        class="task-name"
                                        :title="props.row.name"
                                        :to="{
                                            name: 'appmakerTaskExecute',
                                            params: { app_id: props.row.create_info, project_id: props.row.project.id },
                                            query: { instance_id: props.row.id, template_id: props.row.template_id }
                                        }">
                                        {{props.row.name}}
                                    </router-link>
                                </template>
                                <!-- 状态 -->
                                <template v-else-if="item.id === 'task_status'">
                                    <div class="ui-task-status">
                                        <span :class="executeStatus[props.row.id] && executeStatus[props.row.id].cls"></span>
                                        <span class="task-status-text" v-if="executeStatus[props.row.id]">{{executeStatus[props.row.id].text}}</span>
                                    </div>
                                </template>
                                <!-- 其他 -->
                                <template v-else>
                                    {{ props.row[item.id] || '--' }}
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="100" :fixed="appmakerList.length ? 'right' : false">
                            <template slot-scope="props">
                                <!-- 事后鉴权，后续对接新版权限中心 -->
                                <a
                                    v-if="props.row.template_deleted || props.row.template_source === 'onetime'"
                                    class="task-operation-btn disabled"
                                    data-test-id="taskList_table_reexecuteBtn">
                                    {{$t('再次执行')}}
                                </a>
                                <a
                                    v-else-if="!hasCreateTaskPerm(props.row)"
                                    v-cursor
                                    class="text-permission-disable task-operation-btn"
                                    data-test-id="taskList_table_reexecuteBtn"
                                    @click="onTaskPermissonCheck(['mini_app_create_task'], props.row)">
                                    {{$t('再次执行')}}
                                </a>
                                <a
                                    v-else
                                    v-bk-tooltips.top="$t('复⽤参数值并使⽤流程最新数据重新执行')"
                                    class="task-operation-btn"
                                    data-test-id="taskList_table_reexecuteBtn"
                                    @click="getCreateTaskUrl(props.row)">
                                    {{$t('再次执行')}}
                                </a>
                            </template>
                        </bk-table-column>
                        <div class="empty-data" slot="empty">
                            <NoData
                                :type="searchSelectValue.length ? 'search-empty' : 'empty'"
                                :message="searchSelectValue.length ? $t('搜索结果为空') : ''"
                                @searchClear="searchSelectValue = []">
                            </NoData>
                        </div>
                    </bk-table>
                </div>
            </div>
        </skeleton>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import Skeleton from '@/components/skeleton/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'
    import CancelRequest from '@/api/cancelRequest.js'

    const SEARCH_LIST = [
        {
            id: 'task_id',
            name: 'ID'
        },
        {
            id: 'taskName',
            name: i18n.t('任务名'),
            isDefaultOption: true
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
                { id: 'finished', name: i18n.t('完成') }
            ]
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
            min_width: 200
        },
        {
            id: 'task_status',
            label: i18n.t('状态'),
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
            id: 'category_name',
            label: i18n.t('任务类型'),
            width: 120
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
        }
    ]

    export default {
        name: 'appmakerTaskHome',
        components: {
            Skeleton,
            SearchSelect,
            NoData
        },
        mixins: [permission, task],
        props: ['project_id', 'app_id'],
        data () {
            const {
                page = 1,
                limit = 15,
                start_time = '',
                finish_time = '',
                executor = '',
                statusSync = '',
                taskName = '',
                task_id = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'start_time', name: i18n.t('执行开始'), type: 'dateRange' },
                { id: 'finish_time', name: i18n.t('执行结束'), type: 'dateRange' }
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
                isDeleteDialogShow: false,
                taskBasicInfoLoading: true,
                theDeleteTemplateId: undefined,
                pending: {
                    delete: false,
                    authority: false
                },
                appmakerList: [],
                executeStatus: {}, // 任务执行状态
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                requestData: {
                    executor,
                    statusSync,
                    start_time: start_time ? start_time.split(',') : ['', ''],
                    finish_time: finish_time ? finish_time.split(',') : ['', ''],
                    taskName,
                    task_id
                },
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue,
                tableFields: TABLE_FIELDS.slice(0)
            }
        },
        computed: {
            ...mapState({
                businessTimezone: state => state.businessTimezone,
                viewMode: state => state.view_mode,
                appmakerDetail: state => state.appmaker.appmakerDetail,
                authActions: state => state.project.authActions
            })
        },
        async created () {
            this.getBizBaseInfo()
            await this.getAppmakerList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions('taskList/', [
                'loadTaskList'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'getTaskHasSubTaskList',
                'getTaskHasSubTasks'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async getAppmakerList () {
                this.listLoading = true
                this.executeStatus = {}
                try {
                    const { start_time, finish_time, category, executor, statusSync, taskName, task_id } = this.requestData
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
                        create_method: 'app_maker',
                        create_info: this.app_id,
                        pipeline_instance__name__icontains: taskName || undefined,
                        id: task_id || undefined,
                        category: category || undefined,
                        pipeline_instance__executor__contains: executor || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        pipeline_instance__is_revoked,
                        project__id: this.project_id,
                        is_child_taskflow: false
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
                    if (finish_time && finish_time[0] && finish_time[1]) {
                        if (this.template_source === 'common') {
                            data['pipeline_template__finish_time__gte'] = moment(finish_time[0]).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_template__finish_time__lte'] = moment(finish_time[1]).format('YYYY-MM-DD HH:mm:ss')
                        } else {
                            data['pipeline_instance__finish_time_gte'] = moment.tz(finish_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_instance__finish_time__lte'] = moment.tz(finish_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        }
                    }

                    const source = new CancelRequest()
                    const appmakerListData = await this.loadTaskList({
                        params: data,
                        config: { cancelToken: source.token }
                    })
                    const list = appmakerListData.results
                    // 设置level初始值
                    list.forEach(item => {
                        item.level = 0
                    })
                    const result = await this.setListHaveChild(list)
                    this.appmakerList = result
                    this.pagination.count = appmakerListData.count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', result)
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
                const curTaskList = toolsUtils.deepClone(this.appmakerList)
                const curParent = curTaskList.find(item => item.id === row.id)
                curParent.isOpen = !row.isOpen
                curParent.maxLevel = ''
                // table field
                const curField = this.tableFields.find(item => item.id)
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
                        taskIds.forEach(item => {
                            item.children_id.forEach(ite => {
                                taskIdList.push({
                                    id: ite,
                                    parent_id: item.id,
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
                                    task.root_id = row.id
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
                    this.getExecuteStatus('executeStatus', curTaskList)
                    this.appmakerList = curTaskList
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
                    this.getExecuteStatus('executeStatus', filterArr)
                    this.appmakerList = filterArr
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
            onPageChange (page) {
                this.pagination.current = page
                this.getAppmakerList()
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
                this.requestData = data
                this.pagination.current = 1
                this.updateUrl()
                this.getAppmakerList()
            },
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
                if (this.viewMode === 'appmaker') {
                    const { id, name } = this.appmakerDetail
                    resourceData.mini_app = [{ id, name }]
                }
                const flowKey = task.template_source === 'project' ? 'flow' : 'common_flow'
                resourceData[flowKey] = [{
                    id: task.template_id,
                    name: task.template_name
                }]
                this.applyForPermission(required, [...task.auth_actions, ...this.$store.state.project.authActions], resourceData)
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getAppmakerList()
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
                } else if (['start_time', 'finish_time'].includes(column.property)) {
                    const id = this.tableFields[$index].id
                    const date = this.requestData[id]
                    return <TableRenderHeader
                        name={ column.label }
                        orderShow = { false }
                        dateValue={ date }
                        onDateChange={ data => this.handleDateTimeFilter(data, id) }>
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
            handleDateTimeFilter (date = [], id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                if (date.length) {
                    if (index > -1) {
                        this.searchSelectValue[index].values = date
                    } else {
                        const info = {
                            id,
                            type: 'dateRange',
                            name: id === 'start_time' ? i18n.t('执行开始') : i18n.t('执行结束'),
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
            updateUrl () {
                const { current, limit } = this.pagination
                const { start_time, finish_time, executor, statusSync, taskName, task_id } = this.requestData
                const filterObj = {
                    limit,
                    executor,
                    statusSync,
                    page: current,
                    start_time: start_time && start_time.every(item => item) ? start_time.join(',') : '',
                    finish_time: finish_time && finish_time.every(item => item) ? finish_time.join(',') : '',
                    taskName,
                    task_id
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.replace({ name: 'appmakerTaskHome', params: { project_id: this.project_id }, query })
            },
            hasCreateTaskPerm (task) {
                const authActions = [...task.auth_actions, ...this.authActions, ...this.appmakerDetail.auth_actions]
                return this.hasPermission(['mini_app_create_task'], authActions)
            },
            getCreateTaskUrl (task) {
                const { id, template_id, template_source } = task
                const url = {
                    name: 'appmakerTaskCreate',
                    query: { template_id: template_id, task_id: id, entrance: 'taskflow' },
                    params: { project_id: this.project_id, step: 'selectnode', app_id: this.app_id }
                }
                if (template_source === 'common') {
                    url.query.common = 1
                }
                this.$router.push(url)
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/advancedSearch.scss';
@import '@/scss/task.scss';
@import '@/scss/mixins/scrollbar.scss';

.bk-select-inline,.bk-input-inline {
   display: inline-block;
    width: 260px;
}
.appmaker-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;
    @include scrollbar;
}
.app-search {
    @include advancedSearch;
}
.search-wrapper {
    position: relative;
    height: 32px;
}
.appmaker-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .ui-task-status {
        @include ui-task-status;
    }
    .task-operation-btn {
        color: #3a84ff;
        font-size: 12px;
        cursor: pointer;
        &.disabled {
            color: #cccccc;
            cursor: not-allowed;
        }
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
/deep/.recorded_executor_proxy-label {
        display: flex;
        align-items: center;
        .table-header-tips {
            flex-shrink: 0;
            margin-left: 4px;
            font-size: 14px;
            color: #c4c6cc;
        }
    }
/deep/ .cell .task-id {
    margin-left: 16px;
}
</style>
