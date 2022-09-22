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
                        <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                        <bk-table-column :label="$t('任务名称')" min-width="200">
                            <template slot-scope="props">
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
                        </bk-table-column>
                        <bk-table-column :label="$t('执行开始')" width="200" :render-header="renderTableHeader">
                            <template slot-scope="props">
                                {{ props.row.start_time || '--' }}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('执行结束')" width="200" :render-header="renderTableHeader">
                            <template slot-scope="props">
                                {{ props.row.finish_time || '--' }}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('任务类型')" prop="category_name" width="140"></bk-table-column>
                        <bk-table-column :label="$t('创建人')" prop="creator_name" width="140"></bk-table-column>
                        <bk-table-column :label="$t('执行人')" width="140">
                            <template slot-scope="props">
                                {{ props.row.executor_name || '--' }}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('状态')" width="100">
                            <template slot-scope="props">
                                <div class="ui-task-status">
                                    <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                    <span class="task-status-text" v-if="executeStatus[props.$index]">{{executeStatus[props.$index].text}}</span>
                                </div>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="100" :fixed="appmakerList.length ? 'right' : false">
                            <template slot-scope="props">
                                <a
                                    v-cursor="{ active: !hasPermission(['task_clone'], props.row.auth_actions) }"
                                    :class="['task-operation-btn', {
                                        'text-permission-disable': !hasPermission(['task_clone'], props.row.auth_actions)
                                    }]"
                                    href="javascript:void(0);"
                                    @click="onCloneTaskClick(props.row, $event)">
                                    {{ $t('克隆') }}
                                </a>
                            </template>
                        </bk-table-column>
                        <div class="empty-data" slot="empty"><NoData /></div>
                    </bk-table>
                </div>
            </div>
        </skeleton>
        <TaskCloneDialog
            :is-task-clone-dialog-show="isTaskCloneDialogShow"
            :task-name="theCloneTaskName"
            :pending="pending.clone"
            @confirm="onCloneConfirm"
            @cancel="onCloneCancel">
        </TaskCloneDialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import Skeleton from '@/components/skeleton/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskCloneDialog from '@/pages/task/TaskList/TaskCloneDialog.vue'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'

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

    export default {
        name: 'appmakerTaskHome',
        components: {
            Skeleton,
            TaskCloneDialog,
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
                    authority: false,
                    clone: false
                },
                appmakerList: [],
                executeStatus: [], // 任务执行状态
                isTaskCloneDialogShow: false,
                theCloneTaskId: undefined,
                theCloneTaskName: '',
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
                searchSelectValue
            }
        },
        computed: {
            ...mapState({
                businessTimezone: state => state.businessTimezone
            })
        },
        async created () {
            this.getBizBaseInfo()
            await this.getAppmakerList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions('taskList/', [
                'loadTaskList',
                'cloneTask'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async getAppmakerList () {
                this.listLoading = true
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
                        project__id: this.project_id
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
                    if (finish_time && finish_time[0] && finish_time[1]) {
                        if (this.template_source === 'common') {
                            data['pipeline_template__finish_time__gte'] = moment(finish_time[0]).format('YYYY-MM-DD')
                            data['pipeline_template__finish_time__lte'] = moment(finish_time[1]).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['pipeline_instance__finish_time_gte'] = moment.tz(finish_time[0], this.timeZone).format('YYYY-MM-DD')
                            data['pipeline_instance__finish_time__lte'] = moment.tz(finish_time[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }

                    const appmakerListData = await this.loadTaskList(data)
                    const list = appmakerListData.results
                    this.appmakerList = list
                    this.pagination.count = appmakerListData.count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', list)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
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
                this.applyForPermission(required, [...task.auth_actions, ...this.$store.state.project.authActions], resourceData)
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getAppmakerList()
            },
            renderTableHeader (h, { column, $index }) {
                const id = $index === 2 ? 'start_time' : 'finish_time'
                const date = this.requestData[id]
                return <TableRenderHeader
                    name={ column.label }
                    orderShow = { false }
                    dateValue={ date }
                    onDateChange={ data => this.handleDateTimeFilter(data, id) }>
                </TableRenderHeader>
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
                        name: 'appmakerTaskExecute',
                        params: { app_id: this.app_id, project_id: this.project_id },
                        query: { instance_id: data.data.new_instance_id, template_id: this.$route.query.template_id }
                    })
                } catch (e) {
                    console.log(e)
                }
            },
            onCloneCancel () {
                this.isTaskCloneDialogShow = false
                this.theCloneTaskName = ''
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
    .empty-data {
        padding: 120px 0;
    }
    .ui-task-status {
        @include ui-task-status;
    }
    .task-operation-btn {
        color: #3a84ff;
        font-size: 12px;
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
</style>
