/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
                <advance-search-form
                    id="appmakerHome"
                    :open="isSearchFormOpen"
                    :search-form="searchForm"
                    :search-config="{ placeholder: $t('请输入任务名称') }"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                </advance-search-form>
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
                        <bk-table-column :label="$t('执行开始')" width="200">
                            <template slot-scope="props">
                                {{ props.row.start_time || '--' }}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('执行结束')" width="200">
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
                        <bk-table-column :label="$t('操作')" width="100">
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
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import TaskCloneDialog from '@/pages/task/TaskList/TaskCloneDialog.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'

    const SEARCH_FORM = [
        {
            type: 'dateRange',
            key: 'queryTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('执行开始'),
            value: ['', '']
        },
        {
            type: 'select',
            label: i18n.t('任务分类'),
            key: 'category',
            loading: true,
            placeholder: i18n.t('请选择分类'),
            list: [],
            value: ''
        },
        {
            type: 'input',
            key: 'creator',
            label: i18n.t('创建人'),
            placeholder: i18n.t('请输入创建人'),
            value: ''
        },
        {
            type: 'input',
            key: 'executor',
            label: i18n.t('执行人'),
            placeholder: i18n.t('请输入执行人'),
            value: ''
        },
        {
            type: 'select',
            label: i18n.t('状态'),
            key: 'statusSync',
            loading: false,
            placeholder: i18n.t('请选择状态'),
            list: [
                { 'value': 'nonExecution', 'name': i18n.t('未执行') },
                { 'value': 'runing', 'name': i18n.t('未完成') },
                { 'value': 'finished', 'name': i18n.t('完成') }
            ],
            value: ''
        }
    ]

    export default {
        name: 'appmakerTaskHome',
        components: {
            Skeleton,
            AdvanceSearchForm,
            TaskCloneDialog,
            NoData
        },
        mixins: [permission, task],
        props: ['project_id', 'app_id'],
        data () {
            const {
                page = 1,
                limit = 15,
                category = '',
                queryTime = '',
                statusSync = '',
                creator = '',
                executor = '',
                keyword = ''
            } = this.$route.query
            const searchForm = SEARCH_FORM.map(item => {
                if (this.$route.query[item.key]) {
                    if (Array.isArray(item.value)) {
                        item.value = this.$route.query[item.key].split(',')
                    } else {
                        item.value = this.$route.query[item.key]
                    }
                }
                return item
            })
            const isSearchFormOpen = SEARCH_FORM.some(item => this.$route.query[item.key])

            return {
                firstLoading: true,
                listLoading: false,
                searchForm,
                isSearchFormOpen,
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
                taskCategory: [],
                isTaskCloneDialogShow: false,
                theCloneTaskId: undefined,
                theCloneTaskName: '',
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                statusList: [
                    { 'value': 'nonExecution', 'name': i18n.t('未执行') },
                    { 'value': 'running', 'name': i18n.t('未完成') },
                    { 'value': 'revoked', 'name': i18n.t('撤销') },
                    { 'value': 'finished', 'name': i18n.t('完成') }
                ],
                requestData: {
                    category,
                    creator,
                    executor,
                    statusSync,
                    queryTime: queryTime ? queryTime.split(',') : ['', ''],
                    taskName: keyword
                }
            }
        },
        computed: {
            ...mapState({
                businessTimezone: state => state.businessTimezone
            })
        },
        async created () {
            this.getBizBaseInfo()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
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
                    const { queryTime, category, creator, executor, statusSync, taskName } = this.requestData
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
                        q: taskName,
                        category: category || undefined,
                        pipeline_instance__creator__contains: creator || undefined,
                        pipeline_instance__executor__contains: executor || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        pipeline_instance__is_revoked,
                        project__id: this.project_id
                    }
                    
                    if (queryTime[0] && queryTime[1]) {
                        data['pipeline_instance__start_time__gte'] = moment.tz(queryTime[0], this.businessTimezone).format('YYYY-MM-DD')
                        data['pipeline_instance__start_time__lte'] = moment.tz(queryTime[1], this.businessTimezone).add('1', 'd').format('YYYY-MM-DD')
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
                    this.taskCategory = res.data.task_categories.map(m => ({ value: m.value, name: m.name }))
                    this.setProjectBaseInfo(res.data)
                    this.taskBasicInfoLoading = false
                    const form = this.searchForm.find(item => item.key === 'category')
                    form.list = this.taskCategory
                    form.loading = false
                } catch (e) {
                    console.log(e)
                }
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getAppmakerList()
            },
            searchInputhandler (data) {
                this.requestData.taskName = data
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
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
                this.pagination.current = 1
                this.updateUrl()
                this.getAppmakerList()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getAppmakerList()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { category, queryTime, creator, executor, statusSync, taskName } = this.requestData
                const filterObj = {
                    limit,
                    category,
                    creator,
                    executor,
                    statusSync,
                    page: current,
                    queryTime: queryTime.every(item => item) ? queryTime.join(',') : '',
                    keyword: taskName
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
