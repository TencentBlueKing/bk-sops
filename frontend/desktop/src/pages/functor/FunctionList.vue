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
    <div class="functor-container">
        <skeleton :loading="firstLoading" loader="taskList">
            <div class="list-wrapper">
                <div class="search-wrapper mb20">
                    <bk-button
                        theme="primary"
                        style="min-width: 120px;"
                        data-test-id="function_form_createTaskBtn"
                        @click="onCreateTask">
                        {{$t('新建')}}
                    </bk-button>
                    <span class="operate-wrap" @click.stop>
                        <bk-checkbox class="auto-redraw" v-model="isAutoRedraw" @change="onAutoRedrawChange">{{ $t('实时刷新') }}</bk-checkbox>
                        <bk-button
                            class="my-create-btn"
                            data-test-id="function_form_myCreateProcess"
                            @click="handleMyCreateFilter">
                            {{$t('我创建的')}}
                        </bk-button>
                    </span>
                    <search-select
                        ref="searchSelect"
                        id="functionList"
                        :placeholder="$t('ID/任务名/所属项目/提单人/认领人/认领状态/执行状态')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="functor-table-content" data-test-id="function_table_functionTaskList">
                    <bk-table
                        :data="functorList"
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
                            :width="item.width"
                            :render-header="renderTableHeader"
                            show-overflow-tooltip
                            :min-width="item.min_width">
                            <template slot-scope="props">
                                <!--所属项目-->
                                <div v-if="item.id === 'project'">
                                    <span :title="props.row.task.project.name">{{ props.row.task.project.name }}</span>
                                </div>
                                <!--流程模板-->
                                <div v-else-if="item.id === 'name'">
                                    <a
                                        v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        :title="props.row.task.name"
                                        @click="onTaskPermissonCheck(['task_view'], props.row)">
                                        {{props.row.task.name}}
                                    </a>
                                    <router-link
                                        v-else
                                        class="task-name"
                                        :title="props.row.task.name"
                                        :to="{
                                            name: 'functionTaskExecute',
                                            params: { project_id: props.row.task.project.id },
                                            query: { instance_id: props.row.task.id }
                                        }">
                                        {{props.row.task.name}}
                                    </router-link>
                                </div>
                                <!--认领状态-->
                                <div v-else-if="item.id === 'claim_status'">
                                    <span :class="statusClass(props.row.status)"></span>
                                    {{statusMethod(props.row.status, props.row.status_name)}}
                                </div>
                                <!--执行状态-->
                                <div v-else-if="item.id === 'excute_status'" class="task-status">
                                    <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                    <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                                </div>
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="props.row[item.id] || '--'">{{ props.row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="100">
                            <template slot-scope="props">
                                <template v-if="props.row.status === 'submitted'">
                                    <a
                                        v-if="!hasPermission(['task_claim'], props.row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTaskPermissonCheck(['task_claim'], props.row)">
                                        {{ $t('认领') }}
                                    </a>
                                    <router-link
                                        v-else
                                        class="functor-operation-btn"
                                        :to="{
                                            name: 'functionTaskExecute',
                                            params: { project_id: props.row.task.project.id },
                                            query: { instance_id: props.row.task.id }
                                        }">
                                        {{ $t('认领') }}
                                    </router-link>
                                </template>
                                <template v-else>
                                    <a
                                        v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTaskPermissonCheck(['task_view'], props.row)">
                                        {{ $t('查看') }}
                                    </a>
                                    <router-link
                                        v-else
                                        class="functor-operation-btn"
                                        :to="{
                                            name: 'functionTaskExecute',
                                            params: { project_id: props.row.task.project.id },
                                            query: { instance_id: props.row.task.id }
                                        }">
                                        {{ $t('查看') }}
                                    </router-link>
                                    <span
                                        v-if="props.row.status === 'claimed' && props.row.claimant === username"
                                        v-cursor="{ active: !hasPermission(['task_view'], props.row.auth_actions) }"
                                        :class="['functor-operation-btn', { 'text-permission-disable': !hasPermission(['task_view'], props.row.auth_actions) }]"
                                        style="margin-left: 6px;"
                                        @click="onTransferClick(props.row)">
                                        {{ $t('转交') }}
                                    </span>
                                </template>
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
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="$t('新建')"
            :value="isShowNewTaskDialog"
            data-test-id="function_form_createTaskDialog"
            @confirm="onConfirmlNewTask"
            @cancel="onCancelNewTask">
            <div class="create-task-content">
                <div class="common-form-item" data-test-id="function_form_selectBusiness">
                    <label>{{$t('选择项目')}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="business.id"
                            class="bk-select-inline"
                            :popover-width="430"
                            :searchable="true"
                            :is-loading="business.loading"
                            :placeholder="$t('请选择')"
                            :clearable="true"
                            @clear="onClearBusiness"
                            @selected="onSelectedBusiness">
                            <bk-option
                                v-for="(option, index) in business.list"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                        <span v-show="business.empty" class="common-error-tip error-msg">{{$t('选择项目')}}</span>
                    </div>
                </div>
                <div class="common-form-item" data-test-id="function_form_selectTemplate">
                    <label>{{$t('选择模板')}}</label>
                    <div class="common-form-content">
                        <bk-select
                            ref="tplSelect"
                            v-model="template.id"
                            class="bk-select-inline"
                            :popover-width="260"
                            :is-loading="business.loading"
                            :searchable="template.searchable"
                            :placeholder="$t('请选择')"
                            :clearable="true"
                            :disabled="template.disabled"
                            enable-scroll-load
                            :scroll-loading="{ isLoading: template.loading }"
                            :show-empty="false"
                            :remote-method="onTplSearch"
                            @selected="onSelectedTemplate"
                            @clear="onClearTemplate"
                            @scroll-end="onSelectScrollLoad">
                            <div v-bkloading="{ isLoading: tplSearchLoading, size: 'small', extCls: 'template-loading' }">
                                <bk-option-group
                                    v-for="(group, index) in template.list"
                                    :name="group.name"
                                    :key="index">
                                    <p slot="group-name">
                                        {{ group.name }}
                                        ({{ group.count }})
                                    </p>
                                    <bk-option v-for="childOption in group.children"
                                        :key="childOption.id"
                                        :id="childOption.id"
                                        :name="childOption.name">
                                    </bk-option>
                                </bk-option-group>
                            </div>
                        </bk-select>
                        <i class="common-icon-info template-selector-tips"
                            v-bk-tooltips="{
                                width: 400,
                                placement: 'top',
                                content: $t('如果未找到模板，请联系项目运维在流程模板的使用权限中对你或所有职能化人员授予“新建任务权限”') }"></i>
                        <span v-show="template.empty" class="common-error-tip error-msg">{{$t('选择模板')}}</span>
                    </div>
                </div>
            </div>
            <div slot="footer" class="dialog-footer">
                <bk-button
                    theme="primary"
                    :loading="permissionLoading"
                    :class="{ 'btn-permission-disable': !hasCreateTaskPerm }"
                    v-cursor="{ active: !hasCreateTaskPerm }"
                    data-test-id="function_form_confirmNewTaskBtn"
                    @click="onConfirmlNewTask">
                    {{$t('确认')}}
                </bk-button>
                <bk-button theme="default" data-test-id="function_form_cancelBtn" @click="onCancelNewTask">{{$t('取消')}}</bk-button>
            </div>
        </bk-dialog>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :auto-close="false"
            :header-position="'left'"
            :title="$t('转交')"
            :loading="transferPending"
            :value="isShowTransferDialog"
            @confirm="onTransferConfirm"
            @cancel="onTransferCancel">
            <bk-form ref="transferForm" style="padding: 30px 30px 30px 10px" :model="{ claimant }" :rules="transferRules">
                <bk-form-item label="任务">
                    <div>{{ getTransferTaskName() }}</div>
                </bk-form-item>
                <bk-form-item label="转交人" property="claimant">
                    <member-select v-model="claimant" style="width: 100%;" :multiple="false"></member-select>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapMutations, mapState } from 'vuex'
    import Skeleton from '@/components/skeleton/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
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
            id: 'selectedProject',
            name: i18n.t('所属项目'),
            children: []
        },
        {
            id: 'creator',
            name: i18n.t('提单人')
        },
        {
            id: 'claimant',
            name: i18n.t('认领人')
        },
        {
            id: 'claimStatus',
            name: i18n.t('任务阶段'),
            children: [
                { id: 'submitted', name: i18n.t('未认领') },
                { id: 'claimed', name: i18n.t('已认领') },
                { id: 'executed', name: i18n.t('已执行') },
                { id: 'finished', name: i18n.t('完成') }
            ]
        },
        {
            id: 'statusSync',
            name: i18n.t('执行状态'),
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
            id: 'project',
            label: i18n.t('所属项目'),
            width: 160
        }, {
            id: 'id',
            label: i18n.t('任务ID'),
            width: 110
        }, {
            id: 'name',
            label: i18n.t('任务名称'),
            disabled: true,
            min_width: 200
        }, {
            id: 'create_time',
            label: i18n.t('提单时间'),
            isShow: true,
            width: 200
        }, {
            id: 'claim_time',
            label: i18n.t('认领时间'),
            width: 200
        }, {
            id: 'creator',
            label: i18n.t('提单人'),
            width: 120
        }, {
            id: 'claimant',
            label: i18n.t('认领人'),
            width: 120
        }, {
            id: 'claim_status',
            label: i18n.t('任务阶段'),
            width: 170
        }, {
            id: 'excute_status',
            label: i18n.t('执行状态'),
            width: 120
        }
    ]
    export default {
        name: 'functionHome',
        components: {
            Skeleton,
            NoData,
            MemberSelect,
            SearchSelect
        },
        mixins: [permission, task],
        props: ['project_id', 'app_id'],
        data () {
            const {
                page = 1,
                limit = 15,
                selectedProject = '',
                create_time = '',
                claim_time = '',
                creator = '',
                claimStatus = '',
                statusSync = '',
                taskName = '',
                task_id = '',
                claimant = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'create_time', name: i18n.t('提单时间'), type: 'dateRange' },
                { id: 'claim_time', name: i18n.t('认领时间'), type: 'dateRange' }
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
                functorSync: 0,
                isShowNewTaskDialog: false,
                isShowTransferDialog: false,
                functorBasicInfoLoading: true,
                transferId: '',
                claimant: [],
                transferPending: false,
                functorList: [],
                executeStatus: [], // 任务执行状态
                business: {
                    list: [],
                    loading: false,
                    id: '',
                    searchable: true,
                    empty: false
                },
                template: {
                    list: [
                        {
                            name: i18n.t('项目流程'),
                            count: 0,
                            children: []
                        },
                        {
                            name: i18n.t('公共流程'),
                            count: 0,
                            children: []
                        }
                    ],
                    loading: false,
                    searchable: true,
                    id: '',
                    name: '',
                    project: {},
                    empty: false,
                    disabled: false
                },
                isCommonTemplate: false,
                isAutoRedraw: false,
                autoRedrawTimer: null,
                status: undefined,
                functorCategory: [],
                requestData: {
                    selectedProject,
                    creator,
                    statusSync,
                    claimStatus,
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    claim_time: claim_time ? claim_time.split(',') : ['', ''],
                    taskName,
                    task_id,
                    claimant
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
                permissionLoading: false, // 查询公共流程在项目下的创建任务权限 loading
                tplAction: [],
                hasCreateTaskPerm: true,
                transferRules: {
                    claimant: [{
                        required: true,
                        message: i18n.t('必填项'),
                        trigger: 'blur'
                    }]
                },
                totalPage: 1,
                tplPagination: {
                    current: 1,
                    count: 0,
                    limit: 15
                },
                tplSearchLoading: false,
                flowName: '',
                isLoadCommonTpl: false,
                onTplSearch: null,
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username,
                'categorys': state => state.categorys,
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone
            })
        },
        async created () {
            this.getFields()
            this.loadFunctionTask()
            await this.getProjectList()
            await this.getProjectSearchForm()
            this.firstLoading = false
            this.onTplSearch = toolsUtils.debounce(this.handleTplSearch, 500)
        },
        beforeDestroy () {
            this.clearAutoRedraw()
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('functionTask/', [
                'loadFunctionTaskList',
                'transferFunctionTask'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions('project/', [
                'loadUserProjectList'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm'
            ]),
            async loadFunctionTask () {
                this.listLoading = true
                try {
                    const { selectedProject, create_time, claim_time, creator, statusSync, taskName, claimant, task_id, claimStatus } = this.requestData
                    let task__pipeline_instance__is_started
                    let task__pipeline_instance__is_finished
                    let task__pipeline_instance__is_revoked
                    switch (statusSync) {
                        case 'nonExecution':
                            task__pipeline_instance__is_started = false
                            break
                        case 'running':
                            task__pipeline_instance__is_started = true
                            task__pipeline_instance__is_finished = false
                            task__pipeline_instance__is_revoked = false
                            break
                        case 'revoked':
                            task__pipeline_instance__is_revoked = true
                            break
                        case 'finished':
                            task__pipeline_instance__is_finished = true
                            break
                    }
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        task__pipeline_instance__name__icontains: taskName || undefined,
                        creator: creator || undefined,
                        claimant: claimant || undefined,
                        task__project__id: selectedProject || undefined,
                        status: claimStatus || undefined,
                        id: task_id || undefined,
                        task__pipeline_instance__is_started,
                        task__pipeline_instance__is_finished,
                        task__pipeline_instance__is_revoked
                    }
                    if (create_time && create_time[0] && create_time[1]) {
                        if (this.common) {
                            data['pipeline_template__start_time__gte'] = moment(create_time[0]).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_template__start_time__lte'] = moment(create_time[1]).format('YYYY-MM-DD HH:mm:ss')
                        } else {
                            data['create_time__gte'] = moment.tz(create_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                            data['create_time__lte'] = moment.tz(create_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        }
                    }
                    if (claim_time && claim_time[0] && claim_time[1]) {
                        if (this.common) {
                            data['pipeline_template__claim_time__gte'] = moment(claim_time[0]).format('YYYY-MM-DD HH:mm:ss')
                            data['pipeline_template__claim_time__lte'] = moment(claim_time[1]).format('YYYY-MM-DD HH:mm:ss')
                        } else {
                            data['claim_time__gte'] = moment.tz(claim_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                            data['claim_time__lte'] = moment.tz(claim_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        }
                    }
                    const source = new CancelRequest()
                    const functorListData = await this.loadFunctionTaskList({
                        params: data,
                        config: { cancelToken: source.token }
                    })
                    const list = functorListData.results
                    const taskList = functorListData.results.map(m => m.task)
                    this.functorList = list
                    this.pagination.count = functorListData.count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', taskList)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (['create_time', 'claim_time'].includes(column.property)) {
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
                            name: id === 'create_time' ? i18n.t('提单时间') : i18n.t('认领时间'),
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
                const settingFields = localStorage.getItem('FunctionList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields.map(item => item.id)
                    if (!fieldList || !size) {
                        localStorage.removeItem('FunctionList')
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
                localStorage.setItem('FunctionList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.loadFunctionTask()
                // 重置自动刷新时间
                this.onOpenAutoRedraw()
            },
            onPageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.loadFunctionTask()
                // 重置自动刷新时间
                this.onOpenAutoRedraw()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { selectedProject, create_time, claim_time, creator, statusSync, taskName, task_id, claimant, claimStatus } = this.requestData
                const filterObj = {
                    limit,
                    selectedProject,
                    creator,
                    statusSync,
                    page: current,
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    claim_time: claim_time && claim_time.every(item => item) ? claim_time.join(',') : '',
                    taskName,
                    task_id,
                    claimant,
                    claimStatus
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.replace({ name: 'functionHome', query })
            },
            statusMethod (status, status_name) {
                if (status === 'finished') {
                    return i18n.t('完成')
                } else if (status === 'submitted') {
                    return i18n.t('未认领')
                } else if (status === 'rejected') {
                    return i18n.t('已驳回')
                }
                return status_name
            },
            statusClass (status) {
                let cls
                switch (status) {
                    case 'submitted': // 未认领
                        cls = 'common-icon-flag-circle default'
                        break
                    case 'claimed': // 已认领
                        cls = 'common-icon-flag-circle success'
                        break
                    case 'executed': // 已执行
                        cls = 'common-icon-dark-circle-ellipsis primary'
                        break
                    case 'rejected': // 已驳回
                        cls = 'common-icon-dark-circle-close'
                        break
                    case 'finished': // 完成
                        cls = 'bk-icon icon-check-circle-shape'
                        break
                    default:
                        cls = ''
                }

                return cls
            },
            onCreateTask () {
                this.isShowNewTaskDialog = true
            },
            async getProjectList () {
                this.business.loading = true
                try {
                    const businessData = await this.loadUserProjectList({
                        params: { is_disable: false }
                    })
                    this.business.list = businessData.results
                } catch (e) {
                    console.log(e)
                } finally {
                    this.business.loading = false
                }
            },
            async getProjectSearchForm () {
                try {
                    const businessData = await this.loadUserProjectList()
                    const form = this.searchList.find(item => item.id === 'selectedProject')
                    form.children = businessData.results.map(m => ({ name: m.name, id: m.id }))
                    // 因为项目所属列表是通过接口获取的，所以需要把路径上的标签添加进去
                    const project_id = this.$route.query['selectedProject']
                    if (project_id) {
                        const { id, name, children } = form
                        const values = children.filter(item => String(project_id) === String(item.id))
                        this.searchSelectValue.push({ id, name, values })
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            async getTemplateList (add, isCommon = this.isLoadCommonTpl) {
                try {
                    // 查询职能化数据及公共流程数据
                    const { limit, current } = this.tplPagination
                    const offset = (current - 1) * limit
                    const params = {
                        limit: 15,
                        offset,
                        pipeline_template__name__icontains: this.flowName || undefined
                    }
                    if (isCommon) {
                        params.common = 1
                    } else {
                        params.project__id = this.business.id
                    }
                    const tplListData = await this.loadTemplateList(params)
                    tplListData.results.forEach(item => {
                        item.isCommon = isCommon
                    })

                    // 当项目列表为空或轮到公共流程加载时, 添加公共流程分组
                    if (isCommon && !this.template.list[1]) {
                        this.template.list.push({
                            name: i18n.t('公共流程'),
                            children: tplListData.results
                        })
                    } else if (!isCommon && !tplListData.count) {
                        this.template.list[0].children = []
                    } else {
                        if (add) {
                            this.template.list[isCommon ? 1 : 0].children.push(...tplListData.results)
                        } else {
                            this.template.list[isCommon ? 1 : 0].children = tplListData.results
                        }
                    }
                    this.template.list[isCommon ? 1 : 0].count = tplListData.count
                    this.tplPagination.count = tplListData.count
                    const totalPage = Math.ceil(this.tplPagination.count / limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                    // 项目流程第一次加载时, 移除公共流程分组(为了实现滚动加载)
                    if (!isCommon && current === 1) {
                        this.template.list.splice(1, 1)
                    }

                    // 开始重新加载公共流程列表
                    if (!isCommon && (totalPage === 1 || this.totalPage <= current)) {
                        this.isLoadCommonTpl = true
                        this.resetTplPagination()
                        await this.getTemplateList()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.template.loading = false
                    this.tplSearchLoading = false
                }
            },
            resetTplPagination () {
                this.totalPage = 1
                this.tplPagination = {
                    current: 1,
                    count: 0,
                    limit: 15
                }
            },
            onSelectedBusiness (id) {
                const business = this.business.list.find(item => item.id === id)
                this.business.id = id
                this.business.name = business.name
                this.business.auth_actions = business.auth_actions
                this.isLoadCommonTpl = false
                this.resetTplPagination()
                this.tplSearchLoading = true
                this.getTemplateList()
                this.business.empty = false
                this.template.id = ''
                this.template.name = ''
                this.template.project = {}
                this.template.disabled = false
                this.hasCreateTaskPerm = true
            },
            onSelectedTemplate (id) {
                const templateList = this.template.list
                let isCommon = ''
                let name, project, tplAction

                if (id === undefined) {
                    return
                }

                templateList.some(group => {
                    return group.children.some(item => {
                        if (item.id === id) {
                            isCommon = item.isCommon
                            name = item.name
                            project = item.project
                            tplAction = item.auth_actions
                            return true
                        }
                    })
                })

                this.isCommonTemplate = false
                // 通过isCommon查找是否是公共流程
                this.isCommonTemplate = isCommon
                this.template.id = id
                this.template.name = name
                this.template.project = project
                this.template.empty = false
                this.tplAction = tplAction
                this.checkCreateTaskPerm()
            },
            async checkCreateTaskPerm () {
                if (this.isCommonTemplate) {
                    try {
                        this.permissionLoading = true
                        const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                        const data = {
                            action: 'common_flow_create_task',
                            resources: [
                                {
                                    system: bkSops.id,
                                    type: 'project',
                                    id: this.business.id,
                                    attributes: {}
                                },
                                {
                                    system: bkSops.id,
                                    type: 'common_flow',
                                    id: this.template.id,
                                    attributes: {}
                                }
                            ]
                        }
                        const resp = await this.queryUserPermission(data)
                        this.hasCreateTaskPerm = resp.data.is_allow
                    } catch (e) {
                        console.log(e)
                    } finally {
                        this.permissionLoading = false
                    }
                } else {
                    this.hasCreateTaskPerm = this.hasPermission(['flow_create_task'], this.tplAction)
                }
            },
            applyCreateTaskPerm () {
                let reqPermission = []
                let curPermission = []
                let resourceData = {}
                if (this.isCommonTemplate) {
                    reqPermission = ['common_flow_create_task']
                    curPermission = [...this.tplAction, ...this.business.auth_actions]
                    resourceData = {
                        common_flow: [{
                            id: this.template.id,
                            name: this.template.name
                        }],
                        project: [{
                            id: this.business.id,
                            name: this.business.name
                        }]
                    }
                } else {
                    reqPermission = ['flow_create_task']
                    curPermission = [...this.tplAction]
                    resourceData = {
                        flow: [{
                            id: this.template.id,
                            name: this.template.name
                        }],
                        project: [{
                            id: this.template.project.id,
                            name: this.template.project.name
                        }]
                    }
                }
                this.applyForPermission(reqPermission, curPermission, resourceData)
            },
            onConfirmlNewTask () {
                if (this.business.id === '') {
                    this.business.empty = true
                    return
                }
                if (this.template.id === '') {
                    this.template.empty = true
                    return
                }
                if (this.permissionLoading) {
                    return
                }

                if (!this.hasCreateTaskPerm) {
                    this.applyCreateTaskPerm()
                    return
                }

                if (this.isCommonTemplate) {
                    this.$router.push({
                        name: 'functionTemplateStep',
                        params: { project_id: this.business.id, step: 'selectnode' },
                        query: { template_id: this.template.id, common: 1, entrance: 'function' }
                    })
                } else {
                    this.$router.push({
                        name: 'functionTemplateStep',
                        params: { project_id: this.business.id, step: 'selectnode' },
                        query: { template_id: this.template.id, entrance: 'function' }
                    })
                }
            },
            onCancelNewTask () {
                this.onClearTemplate()
                this.onClearBusiness()
                this.isShowNewTaskDialog = false
                this.business.empty = false
                this.template.empty = false
                this.hasCreateTaskPerm = true
            },
            // 下拉框搜索
            async handleTplSearch (val) {
                this.tplSearchLoading = true
                this.isLoadCommonTpl = false
                this.tplPagination.current = 1
                this.flowName = val
                const optionsDom = document.querySelector('.bk-options')
                optionsDom && optionsDom.scrollTo(0, 0)
                this.getTemplateList(false)
            },
            // 下拉框滚动加载
            onSelectScrollLoad () {
                if (this.totalPage !== this.tplPagination.current) {
                    this.tplPagination.current += 1
                    this.template.loading = true
                    this.getTemplateList(true)
                }
            },
            onClearTemplate () {
                this.template.id = ''
                this.template.name = ''
                this.template.project = {}
                this.isLoadCommonTpl = false
                this.resetTplPagination()
            },
            onClearBusiness () {
                this.business.id = ''
                this.business.auth_actions = []
                this.template.id = ''
                this.template.name = ''
                this.template.project = {}
                this.template.disabled = true
            },
            onTaskPermissonCheck (required, data) {
                const permissionData = {
                    task: [{
                        id: data.task.id,
                        name: data.task.name
                    }],
                    project: [{
                        id: data.task.project.id,
                        name: data.task.project.name
                    }]
                }
                this.applyForPermission(required, data.auth_actions, permissionData)
            },
            handleMyCreateFilter () {
                const creatorInfo = this.searchSelectValue.find(item => item.id === 'creator')
                let info = {}
                if (creatorInfo) {
                    creatorInfo.values = [this.username]
                    info = creatorInfo
                } else {
                    const form = this.searchList.find(item => item.id === 'creator')
                    info = { ...form, values: [this.username] }
                    this.searchSelectValue.push(info)
                }
                // 添加搜索记录
                const searchDom = this.$refs.searchSelect
                searchDom && searchDom.addSearchRecord(info)
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
                this.loadFunctionTask()
            },
            onAutoRedrawChange (val) {
                if (val) {
                    return this.onOpenAutoRedraw()
                }
                this.clearAutoRedraw()
            },
            // 开启自动刷新
            onOpenAutoRedraw () {
                if (!this.isAutoRedraw) {
                    return this.clearAutoRedraw()
                }
                clearTimeout(this.autoRedrawTimer)
                this.autoRedrawTimer = setTimeout(() => {
                    this.loadFunctionTask()
                    this.onOpenAutoRedraw()
                }, 15000)
            },
            // 关闭自动刷新
            clearAutoRedraw () {
                clearTimeout(this.autoRedrawTimer)
                this.autoRedrawTimer = null
                this.isAutoRedraw = false
            },
            getTransferTaskName () {
                const funcItem = this.functorList.find(item => item.id === this.transferId)
                return funcItem ? funcItem.task.name : ''
            },
            onTransferClick (data) {
                if (!this.hasPermission(['task_view'], data.auth_actions)) {
                    const permissionData = {
                        task: [{
                            id: data.task.id,
                            name: data.task.name
                        }],
                        project: [{
                            id: data.task.project.id,
                            name: data.task.project.name
                        }]
                    }
                    this.applyForPermission(['task_view'], data.auth_actions, permissionData)
                    return
                }
                this.isShowTransferDialog = true
                this.transferId = data.id
            },
            onTransferConfirm () {
                if (this.transferPending) {
                    return
                }
                this.$refs.transferForm.validate().then(async (result) => {
                    try {
                        this.transferPending = true
                        const params = {
                            claimant: this.claimant[0],
                            id: this.transferId
                        }
                        await this.transferFunctionTask(params)
                        this.isShowTransferDialog = false
                        this.claimant = []
                        this.transferId = ''
                        this.loadFunctionTask()
                    } catch (e) {
                        console.error(e)
                    } finally {
                        this.transferPending = false
                    }
                })
            },
            onTransferCancel () {
                this.isShowTransferDialog = false
                this.claimant = []
                this.transferId = ''
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/task.scss';
@import '@/scss/mixins/scrollbar.scss';

.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.search-wrapper {
    position: relative;
    display: flex;
    justify-content: space-between;
    .operate-wrap {
        position: absolute;
        right: 495px;
        .my-create-btn {
            margin-left: 15px;
        }
    }
}
.functor-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;
    @include scrollbar;
}
.advanced-search {
    margin: 0;
}

.functor-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .functor-operation-btn {
        color: #3a84ff;
        font-size: 12px;
        cursor: pointer;
    }
    .task-status {
       @include ui-task-status;
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
.icon-check-circle-shape {
    color: $greenDefault;
}
.common-icon-dark-circle-close {
    color: $redDefault;
}
.default {
    color: #979ba5;
}
.primary {
    color: #3a84ff;
}
.success {
    color: #2dcb56;
}
.create-task-content {
    padding: 30px;
    .common-form-item {
        label {
            width: 70px;
            font-weight: normal;
        }
        .common-form-content {
            position: relative;
            margin-left: 80px;
            margin-right: 30px;
            .template-selector-tips {
                position: absolute;
                right: -20px;
                top: 9px;
                color: #c4c6cc;
                cursor: pointer;
                &:hover {
                    color: #f4aa1a;
                }
            }
        }
    }
    .bk-select-inline {
        width: 430px;
    }
}
.dialog-footer {
    .bk-button {
        margin-left: 10px;
        width: 90px;
    }
}
</style>
