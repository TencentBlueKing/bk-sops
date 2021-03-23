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
    <div class="audit-container">
        <div class="list-wrapper">
            <base-title :title="$t('审计中心')"></base-title>
            <div class="operation-area clearfix">
                <advance-search-form
                    id="auditList"
                    :open="isSearchFormOpen"
                    :search-config="{ placeholder: $t('请输入任务名称') }"
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                </advance-search-form>
            </div>
            <div class="audit-table-content">
                <bk-table
                    :data="auditList"
                    :pagination="pagination"
                    :size="setting.size"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }"
                    @page-change="onPageChange"
                    @page-limit-change="onPageLimitChange">
                    <bk-table-column
                        v-for="item in setting.selectedFields"
                        :key="item.id"
                        :label="item.label"
                        :prop="item.id"
                        :width="item.width"
                        :min-width="item.min_width">
                        <template slot-scope="props">
                            <!--所属项目-->
                            <div v-if="item.id === 'project'">
                                <span :title="props.row.project.name">{{ props.row.project.name }}</span>
                            </div>
                            <!--任务名称-->
                            <div v-else-if="item.id === 'name'">
                                <a
                                    v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                    v-cursor
                                    class="text-permission-disable"
                                    :title="props.row.name"
                                    @click="onTemplatePermissonCheck(props.row)">
                                    {{props.row.name}}
                                </a>
                                <router-link
                                    v-else
                                    class="task-name"
                                    :title="props.row.name"
                                    :to="{
                                        name: 'auditTaskExecute',
                                        params: { project_id: props.row.project.id },
                                        query: { instance_id: props.row.id }
                                    }">
                                    {{props.row.name}}
                                </router-link>
                            </div>
                            <!--状态-->
                            <div v-else-if="item.id === 'audit_status'" class="audit-status">
                                <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                <span class="task-status-text" v-if="executeStatus[props.$index]">{{executeStatus[props.$index].text}}</span>
                            </div>
                            <!-- 其他 -->
                            <template v-else>
                                <span :title="props.row[item.id] || '--'">{{ props.row[item.id] || '--' }}</span>
                            </template>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('操作')" width="100">
                        <template slot-scope="props">
                            <a
                                v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                v-cursor
                                class="text-permission-disable"
                                @click="onTemplatePermissonCheck(props.row)">
                                {{$t('查看')}}
                            </a>
                            <router-link
                                v-else
                                class="audit-operation-btn"
                                :to="{
                                    name: 'auditTaskExecute',
                                    params: { project_id: props.row.project.id },
                                    query: { instance_id: props.row.id }
                                }">
                                {{ $t('查看') }}
                            </router-link>
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
                    <div class="empty-data" slot="empty"><NoData /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import task from '@/mixins/task.js'
    const SEARCH_FORM = [
        {
            type: 'select',
            label: i18n.t('所属项目'),
            key: 'selectedProject',
            loading: true,
            placeholder: i18n.t('请选择所属项目'),
            list: [],
            value: ''
        },
        {
            type: 'dateRange',
            key: 'executeTime',
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
                { 'value': 'running', 'name': i18n.t('未完成') },
                { 'value': 'revoked', 'name': i18n.t('撤销') },
                { 'value': 'finished', 'name': i18n.t('完成') }
            ],
            value: ''
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
            disabled: true,
            width: 80
        }, {
            id: 'project',
            label: i18n.t('所属项目'),
            disabled: true,
            width: 120
        }, {
            id: 'name',
            label: i18n.t('任务名称'),
            disabled: true,
            min_width: 200
        }, {
            id: 'start_time',
            label: i18n.t('执行开始'),
            width: 200
        }, {
            id: 'finish_time',
            label: i18n.t('执行结束'),
            width: 200
        }, {
            id: 'category_name',
            label: i18n.t('任务类型'),
            width: 140
        }, {
            id: 'creator_name',
            label: i18n.t('创建人'),
            width: 140
        }, {
            id: 'executor_name',
            label: i18n.t('执行人'),
            width: 140
        }, {
            id: 'audit_status',
            label: i18n.t('状态'),
            width: 120
        }
    ]
    export default {
        name: 'auditHome',
        components: {
            AdvanceSearchForm,
            CopyrightFooter,
            BaseTitle,
            NoData
        },
        mixins: [permission, task],
        data () {
            const {
                page = 1,
                limit = 15,
                selectedProject = '',
                category = '',
                executeTime = '',
                creator = '',
                executor = '',
                statusSync = '',
                keyword = ''
            } = this.$route.query
            const searchForm = SEARCH_FORM.map(item => {
                if (this.$route.query[item.key]) {
                    if (Array.isArray(item.value)) {
                        item.value = this.$route.query[item.key].split(',')
                    } else {
                        item.value = item.key === 'selectedProject' ? Number(this.$route.query[item.key]) : this.$route.query[item.key]
                    }
                }
                return item
            })
            const isSearchFormOpen = SEARCH_FORM.some(item => this.$route.query[item.key])
            return {
                taskBasicInfoLoading: true,
                listLoading: true,
                activeTaskCategory: undefined,
                business: {
                    list: [],
                    loading: false,
                    id: null,
                    searchable: true,
                    empty: false
                },
                searchForm,
                isSearchFormOpen,
                auditList: [],
                taskCategory: [],
                executeStatus: [], // 任务执行态
                requestData: {
                    selectedProject,
                    category,
                    creator,
                    executor,
                    statusSync,
                    executeTime: executeTime ? executeTime.split(',') : ['', ''],
                    taskName: keyword
                },
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                tableFields: TABLE_FIELDS,
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                }
            }
        },
        computed: {
            ...mapState('project', {
                'timeZone': state => state.timezone
            })
        },
        created () {
            this.getFields()
            this.loadAuditTask()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
            this.getProjectList()
            this.getProjectBaseInfo()
        },
        methods: {
            ...mapActions('auditTask/', [
                'loadAuditTaskList'
            ]),
            ...mapActions('task/', [
                'getInstanceStatus'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('project/', [
                'loadUserProjectList'
            ]),
            async loadAuditTask () {
                this.listLoading = true
                try {
                    const { selectedProject, executeTime, category, creator, executor, statusSync, taskName } = this.requestData
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
                        project__id: selectedProject || undefined,
                        category: category || undefined,
                        pipeline_instance__name__contains: taskName || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        pipeline_instance__is_revoked,
                        pipeline_instance__creator__contains: creator || undefined,
                        pipeline_instance__executor__contains: executor || undefined
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
                    const auditListData = await this.loadAuditTaskList(data)
                    const list = auditListData.objects
                    this.auditList = list
                    this.pagination.count = auditListData.meta.total_count
                    this.totalCount = auditListData.meta.total_count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', list)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.listLoading = false
                }
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('AuditList')
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size
                    this.setting.selectedFields = this.tableFields.slice(0).filter(m => fieldList.includes(m.id))
                }
            },
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('AuditList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.loadAuditTask()
            },
            onPageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.loadAuditTask()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { selectedProject, category, executeTime, creator, executor, statusSync, taskName } = this.requestData
                const filterObj = {
                    limit,
                    selectedProject,
                    category,
                    creator,
                    executor,
                    statusSync,
                    page: current,
                    executeTime: executeTime.every(item => item) ? executeTime.join(',') : '',
                    keyword: taskName
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.push({ name: 'auditHome', query })
            },
            searchInputhandler (data) {
                this.requestData.taskName = data
                this.pagination.current = 1
                this.loadAuditTask()
            },
            async getProjectList () {
                this.business.loading = true
                try {
                    const businessData = await this.loadUserProjectList({ limit: 0 })
                    this.business.list = businessData.objects
                    const form = this.searchForm.find(item => item.key === 'selectedProject')
                    form.list = this.business.list.map(m => ({ name: m.name, value: m.id }))
                    form.loading = false
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.business.loading = false
                }
            },
            async getProjectBaseInfo () {
                this.taskBasicInfoLoading = true
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.taskCategory = res.data.task_categories.map(m => ({ name: m.name, value: m.value }))
                    const form = this.searchForm.find(item => item.key === 'category')
                    form.list = this.taskCategory
                    form.loading = false
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskBasicInfoLoading = false
                }
            },
            onClearCategory () {
                this.activeTaskCategory = undefined
            },
            onSelectedCategory (id) {
                this.activeTaskCategory = id
            },
            onTemplatePermissonCheck (task) {
                if (!this.hasPermission(['task_view'], task.auth_actions)) {
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
                }
            },
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
                this.pagination.current = 1
                this.updateUrl()
                this.loadAuditTask()
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/task.scss';
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.audit-container {
    min-width: 1320px;
    min-height: calc(100% - 50px);
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
    .advanced-search {
        margin: 0;
    }
}
.operation-area {
    margin: 20px 0;
    .common-icon-search {
        position: absolute;
        right: 15px;
        top: 8px;
        color: $commonBorderColor;
    }
}
.common-icon-dark-circle-pause {
    color: #ff9C01;
    font-size: 12px;
}
.audit-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .audit-status {
        @include ui-task-status;
    }
    .audit-operation-btn {
        color: #3a84ff;
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
