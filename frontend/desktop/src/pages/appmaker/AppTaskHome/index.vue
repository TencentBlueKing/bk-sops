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
            <base-title :title="$t('任务记录')"></base-title>
            <div class="operation-area clearfix">
                <advance-search-form
                    :search-form="searchForm"
                    :search-config="{ placeholder: $t('请输入任务名称') }"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                </advance-search-form>
            </div>
            <div class="appmaker-table-content">
                <bk-table
                    :data="appmakerList"
                    :pagination="pagination"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }"
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
                                @click="onTaskPermissonCheck(props.row)">
                                {{props.row.name}}
                            </a>
                            <router-link
                                v-else
                                class="task-name"
                                :title="props.row.name"
                                :to="{
                                    name: 'appmakerTaskExecute',
                                    params: { app_id: props.row.create_info, project_id: props.row.project.id },
                                    query: { instance_id: props.row.id }
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
                    <div class="empty-data" slot="empty"><NoData /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'
    const searchForm = [
        {
            type: 'dateRange',
            key: 'queryTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('执行开始'),
            value: []
        },
        {
            type: 'select',
            label: i18n.t('任务分类'),
            key: 'category',
            loading: false,
            placeholder: i18n.t('请选择分类'),
            list: []
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
            ]
        }
    ]
    export default {
        name: 'appmakerTaskHome',
        components: {
            AdvanceSearchForm,
            CopyrightFooter,
            BaseTitle,
            NoData
        },
        mixins: [permission, task],
        props: ['project_id', 'app_id'],
        data () {
            return {
                listLoading: true,
                isDeleteDialogShow: false,
                taskBasicInfoLoading: true,
                theDeleteTemplateId: undefined,
                pending: {
                    delete: false,
                    authority: false
                },
                appmakerList: [],
                executeStatus: [], // 任务执行状态
                taskCategory: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
                },
                statusList: [
                    { 'value': 'nonExecution', 'name': i18n.t('未执行') },
                    { 'value': 'runing', 'name': i18n.t('未完成') },
                    { 'value': 'finished', 'name': i18n.t('完成') }
                ],
                requestData: {
                    queryTime: [],
                    category: '',
                    creator: '',
                    executor: '',
                    statusSync: '',
                    flowName: ''
                }
            }
        },
        computed: {
            ...mapState({
                businessTimezone: state => state.businessTimezone
            }),
            searchForm () {
                const value = searchForm
                value[1].list = this.taskCategory
                value[0].loading = this.taskBasicInfoLoading
                return searchForm
            }
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
                'loadProjectBaseInfo'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async getAppmakerList () {
                this.listLoading = true
                try {
                    const { queryTime, category, creator, executor, statusSync, flowName } = this.requestData
                    let pipeline_instance__is_started
                    let pipeline_instance__is_finished
                    if (statusSync) {
                        pipeline_instance__is_started = statusSync !== 'nonExecution'
                        pipeline_instance__is_finished = statusSync === 'finished'
                    }
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        create_method: 'app_maker',
                        create_info: this.app_id,
                        q: flowName,
                        category: category || undefined,
                        pipeline_instance__creator__contains: creator || undefined,
                        pipeline_instance__executor__contains: executor || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        project__id: this.project_id
                    }
                    
                    if (queryTime[0] && queryTime[1]) {
                        data['pipeline_instance__start_time__gte'] = moment.tz(queryTime[0], this.businessTimezone).format('YYYY-MM-DD')
                        data['pipeline_instance__start_time__lte'] = moment.tz(queryTime[1], this.businessTimezone).add('1', 'd').format('YYYY-MM-DD')
                    }
                    
                    const appmakerListData = await this.loadTaskList(data)
                    const list = appmakerListData.objects
                    this.appmakerList = list
                    this.pagination.count = appmakerListData.meta.total_count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', list)
                } catch (e) {
                    errorHandler(e, this)
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
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getAppmakerList()
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.getAppmakerList()
            },
            onTaskPermissonCheck (task) {
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
                this.applyForPermission(['task_view'], task.auth_actions, resourceData)
            },
            onSearchFormSubmit (data) {
                this.requestData = data
                this.pagination.current = 1
                this.getAppmakerList()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getAppmakerList()
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/advancedSearch.scss';
@import '@/scss/task.scss';
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
