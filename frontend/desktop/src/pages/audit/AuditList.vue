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
    <div class="audit-container">
        <skeleton :loading="firstLoading" loader="commonList">
            <div class="list-wrapper">
                <div class="search-wrapper mb20">
                    <search-select
                        ref="searchSelect"
                        id="auditList"
                        :placeholder="$t('ID/任务名/所属项目/创建人/执行人/状态')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="audit-table-content" data-test-id="aduit_table_auditList">
                    <bk-table
                        :data="auditList"
                        :pagination="pagination"
                        :size="setting.size"
                        :max-height="tableMaxHeight"
                        v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }"
                        @page-change="onPageChange"
                        @page-limit-change="onPageLimitChange">
                        <bk-table-column
                            v-for="item in setting.selectedFields"
                            :key="item.id"
                            :label="item.label"
                            :prop="item.id"
                            :width="item.width"
                            :render-header="renderTableHeader"
                            show-overflow-tooltip
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
                                    <span :class="executeStatus[props.row.id] && executeStatus[props.row.id].cls"></span>
                                    <span class="task-status-text" v-if="executeStatus[props.row.id]">{{executeStatus[props.row.id].text}}</span>
                                </div>
                                <!--任务类型-->
                                <div v-else-if="item.id === 'category_name'">
                                    {{ props.row.flow_type === 'common_func' ? $t('task_职能化') : $t('常规') }}
                                </div>
                                <template v-else-if="isMultiTenantMode">
                                    <bk-user-display-name v-if="item.id === 'creator_name'" :user-id="props.row.creator_name" />
                                    <bk-user-display-name v-else-if="item.id === 'executor_name'" :user-id="props.row.executor_name" />
                                </template>
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
    import { mapState, mapActions } from 'vuex'
    import permission from '@/mixins/permission.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import task from '@/mixins/task.js'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
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
            id: 'selectedProject',
            name: i18n.t('所属项目'),
            children: []
        },
        {
            id: 'creator',
            name: i18n.t('创建人'),
            isUser: true
        },
        {
            id: 'executor',
            name: i18n.t('执行人'),
            isUser: true
        },
        {
            id: 'statusSync',
            name: i18n.t('状态'),
            children: [
                { id: 'nonExecution', name: i18n.t('未执行') },
                { id: 'running', name: i18n.t('未完成') },
                { id: 'revoked', name: i18n.t('终止') },
                { id: 'finished', name: i18n.t('完成') }
            ]
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
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
            Skeleton,
            NoData,
            SearchSelect
        },
        mixins: [permission, task],
        data () {
            const {
                page = 1,
                limit = 15,
                selectedProject = '',
                category = '',
                start_time = '',
                finish_time = '',
                creator = '',
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
                activeTaskCategory: undefined,
                business: {
                    list: [],
                    loading: false,
                    id: null,
                    searchable: true,
                    empty: false
                },
                auditList: [],
                executeStatus: {}, // 任务执行态
                requestData: {
                    selectedProject,
                    category,
                    creator,
                    executor,
                    statusSync,
                    start_time: start_time ? start_time.split(',') : ['', ''],
                    finish_time: finish_time ? finish_time.split(',') : ['', ''],
                    taskName,
                    task_id
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
                },
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue,
                tableMaxHeight: window.innerHeight - 144
            }
        },
        computed: {
            ...mapState({
                isMultiTenantMode: state => state.isMultiTenantMode
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone
            })
        },
        async created () {
            this.getFields()
            this.loadAuditTask()
            await this.getProjectList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions('auditTask/', [
                'loadAuditTaskList'
            ]),
            ...mapActions('project/', [
                'loadUserProjectList'
            ]),
            async loadAuditTask () {
                this.listLoading = true
                this.executeStatus = {}
                try {
                    const { selectedProject, start_time, finish_time, category, creator, executor, statusSync, taskName, task_id } = this.requestData
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
                        user_type: 'auditor',
                        pipeline_instance__name__icontains: taskName || undefined,
                        pipeline_instance__is_started,
                        pipeline_instance__is_finished,
                        pipeline_instance__is_revoked,
                        pipeline_instance__creator__contains: creator || undefined,
                        pipeline_instance__executor__contains: executor || undefined,
                        id: task_id || undefined
                    }
                    if (start_time && start_time[0] && start_time[1]) {
                        if (this.common) {
                            data['pipeline_template__start_time__gte'] = moment(start_time[0]).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_template__start_time__lte'] = moment(start_time[1]).format('YYYY-MM-DD HH:mm:ss')
                        } else {
                            data['pipeline_instance__start_time__gte'] = moment.tz(start_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_instance__start_time__lte'] = moment.tz(start_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        }
                    }
                    if (finish_time && finish_time[0] && finish_time[1]) {
                        if (this.common) {
                            data['pipeline_template__finish_time__gte'] = moment(finish_time[0]).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_template__finish_time__lte'] = moment(finish_time[1]).format('YYYY-MM-DD HH:mm:ss')
                        } else {
                            data['pipeline_instance__finish_time__gte'] = moment.tz(finish_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_instance__finish_time__lte'] = moment.tz(finish_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        }
                    }
                    const source = new CancelRequest()
                    const auditListData = await this.loadAuditTaskList({
                        params: data,
                        config: { cancelToken: source.token }
                    })
                    const list = auditListData.results
                    this.auditList = list
                    this.pagination.count = auditListData.count
                    this.totalCount = auditListData.count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', list)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (['start_time', 'finish_time'].includes(column.property)) {
                    const id = this.setting.selectedFields[$index].id
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
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('AuditList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields.map(item => item.id)
                    if (!fieldList || !size) {
                        localStorage.removeItem('AuditList')
                    }
                } else {
                    selectedFields = this.tableFields.map(item => item.id)
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
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
                const { selectedProject, category, start_time, finish_time, creator, executor, statusSync, taskName, task_id } = this.requestData
                const filterObj = {
                    limit,
                    selectedProject,
                    category,
                    creator,
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
                this.$router.replace({ name: 'auditHome', query })
            },
            handleSearchValueChange (data) {
                data = data.reduce((acc, cur) => {
                    if (cur.type === 'dateRange') {
                        acc[cur.id] = cur.values
                    } else if (cur.multiable) {
                        acc[cur.id] = cur.values.map(item => item.id)
                    } else {
                        const value = cur.values[0]
                        acc[cur.id] = typeof value === 'string' ? value : value.id
                    }
                    return acc
                }, {})
                this.requestData = data
                this.pagination.current = 1
                this.updateUrl()
                this.loadAuditTask()
            },
            async getProjectList () {
                this.business.loading = true
                try {
                    const businessData = await this.loadUserProjectList()
                    this.business.list = businessData.results
                    const form = this.searchList.find(item => item.id === 'selectedProject')
                    form.children = this.business.list.map(m => ({ name: m.name, id: m.id }))
                    // 因为项目所属列表是通过接口获取的，所以需要把路径上的标签添加进去
                    const project_id = this.$route.query['selectedProject']
                    if (project_id) {
                        const { id, name, children } = form
                        const values = children.filter(item => String(project_id) === String(item.id))
                        this.searchSelectValue.push({ id, name, values })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.business.loading = false
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
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/task.scss';
@import '@/scss/mixins/scrollbar.scss';

.audit-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;
    @include scrollbar;
}
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.search-wrapper {
    position: relative;
    height: 32px;
}
.list-wrapper {
    .advanced-search {
        margin: 0;
    }
}
.common-icon-dark-circle-pause {
    color: #ff9c01;
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
