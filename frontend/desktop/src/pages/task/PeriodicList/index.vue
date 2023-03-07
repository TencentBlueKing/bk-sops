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
    <div class="periodic-container">
        <skeleton :loading="firstLoading" loader="taskList">
            <div class="list-wrapper">
                <div class="search-wrapper mb20">
                    <bk-button
                        v-if="!adminView"
                        ref="childComponent"
                        theme="primary"
                        size="normal"
                        style="min-width: 120px;"
                        data-test-id="periodicList_form_createTask"
                        @click="onCreatePeriodTask">
                        {{$t('新建')}}
                    </bk-button>
                    <search-select
                        ref="searchSelect"
                        id="periodicList"
                        :placeholder="$t('ID/任务名/创建人/更新人/状态')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="periodic-table-content" data-test-id="periodicList_table_taskList">
                    <bk-table
                        :data="periodicList"
                        :pagination="pagination"
                        :size="setting.size"
                        @page-change="onPageChange"
                        @page-limit-change="handlePageLimitChange"
                        v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }">
                        <template v-for="item in setting.selectedFields">
                            <bk-table-column
                                v-if="item.isShow ? adminView : true"
                                :key="item.id"
                                :label="item.label"
                                :prop="item.id"
                                :width="item.width"
                                :render-header="renderTableHeader"
                                show-overflow-tooltip
                                :min-width="item.min_width">
                                <template slot-scope="{ row }">
                                    <!--任务-->
                                    <div v-if="item.id === 'name'" class="task-name">
                                        <a
                                            v-if="!adminView"
                                            data-test-id="periodic_task_collectBtn"
                                            v-cursor="{ active: !hasPermission(['periodic_task_edit'], row.auth_actions) }"
                                            href="javascript:void(0);"
                                            class="common-icon-favorite icon-favorite"
                                            :class="{
                                                'is-active': row.is_collected,
                                                'disable': collectingId === row.id,
                                                'text-permission-disable': !hasPermission(['periodic_task_edit'], row.auth_actions)
                                            }"
                                            @click="onCollectTask(row)">
                                        </a>
                                        <span class="name" :title="row.name">{{row.name || '--'}}</span>
                                        <span
                                            class="label"
                                            v-if="row.is_latest === null"
                                            v-bk-tooltips="{ content: '当前任务为旧版周期任务，无法判断创建周期任务后流程数据是否变更。可前往编辑任务，完成一次更新即升级到新版本，获得新版本的提示更新能力。', width: 440 }">
                                            {{ $t('旧版') }}
                                        </span>
                                    </div>
                                    <!--流程模板-->
                                    <div v-else-if="item.id === 'process_template'" class="template-name">
                                        <a
                                            v-if="!hasPermission(['periodic_task_view'], row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            @click="onPeriodicPermissonCheck(['periodic_task_view'], row, $event)">
                                            {{row.task_template_name}}
                                        </a>
                                        <router-link
                                            v-else
                                            class="periodic-name"
                                            target="_blank"
                                            :title="row.task_template_name"
                                            :to="templateNameUrl(row)">
                                            {{row.task_template_name}}
                                        </router-link>
                                        <i
                                            v-if="row.is_latest === false"
                                            :class="['common-icon-update', {
                                                'text-permission-disable': !hasPermission(['periodic_task_edit'], row.auth_actions)
                                            }]"
                                            v-cursor="{ active: !hasPermission(['periodic_task_edit'], row.auth_actions) }"
                                            v-bk-tooltips="$t('流程待更新')"
                                            @click="onModifyCronPeriodic(row, $event)">
                                        </i>
                                    </div>
                                    <!--项目-->
                                    <div v-else-if="item.id === 'project'">
                                        <span :title="row.project.name">{{ row.project.name }}</span>
                                    </div>
                                    <!--周期规则-->
                                    <div v-else-if="item.id === 'cron'">
                                        <div :title="splitPeriodicCron(row.cron)">{{ splitPeriodicCron(row.cron) }}</div>
                                    </div>
                                    <!-- 其他 -->
                                    <template v-else>
                                        <span :title="row[item.id] || '--'">{{ row[item.id] || '--' }}</span>
                                    </template>
                                </template>
                            </bk-table-column>
                        </template>
                        <bk-table-column :label="$t('操作')" width="220" :fixed="periodicList.length ? 'right' : false">
                            <template slot-scope="props">
                                <div class="periodic-operation" :periodic-task-name="props.row.name">
                                    <template v-if="!adminView">
                                        <bk-switcher
                                            :value="props.row.enabled"
                                            v-bk-tooltips.top="props.row.enabled ? $t('暂停') : $t('启动')"
                                            v-cursor="{ active: !hasPermission(['periodic_task_edit'], props.row.auth_actions) }"
                                            :disabled="!hasPermission(['periodic_task_edit'], props.row.auth_actions)"
                                            data-test-id="periodicList_table_enableBtn"
                                            theme="primary"
                                            size="small"
                                            @change="onSetEnable(props.row, $event)">
                                        </bk-switcher>
                                        <a
                                            v-cursor="{ active: !hasPermission(getEditPerm(props.row), props.row.auth_actions) }"
                                            href="javascript:void(0);"
                                            :class="['periodic-bk-btn', {
                                                'clocked-bk-disable': judgeOldCommonPeriodic(props.row),
                                                'text-permission-disable': !hasPermission(getEditPerm(props.row), props.row.auth_actions)
                                            }]"
                                            v-bk-tooltips.top="{
                                                content: $t('不再支持周期任务使用公共流程，请使用项目流程'),
                                                disabled: !hasPermission(getEditPerm(props.row), props.row.auth_actions) || !judgeOldCommonPeriodic(props.row)
                                            }"
                                            data-test-id="periodicList_table_editBtn"
                                            @click="onModifyCronPeriodic(props.row, $event)">
                                            {{ $t('编辑') }}
                                        </a>
                                        <a
                                            v-cursor="{ active: !hasPermission(['periodic_task_delete'], props.row.auth_actions) }"
                                            href="javascript:void(0);"
                                            :class="{
                                                'text-permission-disable': !hasPermission(['periodic_task_delete'], props.row.auth_actions)
                                            }"
                                            data-test-id="periodicList_table_deleteBtn"
                                            @click="onDeletePeriodic(props.row, $event)">
                                            {{ $t('删除') }}
                                        </a>
                                    </template>
                                    <a
                                        v-else
                                        href="javascript:void(0);"
                                        data-test-id="periodicList_table_recordBtn"
                                        @click="onRecordView(props.row, $event)">
                                        {{ $t('启动记录') }}
                                    </a>
                                    <router-link
                                        data-test-id="process_table_executeHistoryBtn"
                                        :to="{
                                            name: 'taskList',
                                            params: { project_id: props.row.project.id },
                                            query: { template_id: props.row.template_id, create_method: 'periodic', create_info: props.row.task.id, template_source: props.row.template_source }
                                        }">
                                        {{ $t('执行历史') }}
                                    </router-link>
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
                </div>
            </div>
        </skeleton>
        <TaskCreateDialog
            :entrance="'periodicTask'"
            :project_id="project_id"
            :is-new-task-dialog-show="isNewTaskDialogShow"
            :business-info-loading="businessInfoLoading"
            :task-category="taskCategory"
            :dialog-title="$t('新建周期任务')"
            @onCreateTaskCancel="onCreateTaskCancel">
        </TaskCreateDialog>
        <ModifyPeriodicDialog
            v-if="isModifyDialogShow"
            :loading="modifyDialogLoading"
            :constants="constants"
            :cron="selectedCron"
            :task-id="selectedPeriodicId"
            :is-modify-dialog-show="isModifyDialogShow"
            :project_id="projectId"
            :cur-row="curRow"
            :is-edit="editTask"
            @onUpdateTask="onUpdateTask"
            @onConfirmSave="onModifyPeriodicConfirm"
            @onCancelSave="onModifyPeriodicCancel">
        </ModifyPeriodicDialog>
        <BootRecordDialog
            :show="isBootRecordDialogShow"
            :id="selectedPeriodicId"
            @onClose="isBootRecordDialogShow = false">
        </BootRecordDialog>
        <DeletePeriodicDialog
            :is-delete-dialog-show="isDeleteDialogShow"
            :template-name="selectedTemplateName"
            :deleting="deleting"
            @onDeletePeriodicConfirm="onDeletePeriodicConfirm"
            @onDeletePeriodicCancel="onDeletePeriodicCancel">
        </DeletePeriodicDialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskCreateDialog from '../../task/TaskList/TaskCreateDialog.vue'
    import ModifyPeriodicDialog from './ModifyPeriodicDialog.vue'
    import BootRecordDialog from './BootRecordDialog.vue'
    import DeletePeriodicDialog from './DeletePeriodicDialog.vue'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import moment from 'moment-timezone'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
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
            id: 'creator',
            name: i18n.t('创建人')
        },
        {
            id: 'editor',
            name: i18n.t('更新人')
        },
        {
            id: 'enabled',
            name: i18n.t('状态'),
            children: [
                { id: 'true', name: i18n.t('启动') },
                { id: 'false', name: i18n.t('暂停') }
            ]
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
            width: 80
        }, {
            id: 'name',
            label: i18n.t('任务名称'),
            disabled: true,
            min_width: 200
        }, {
            id: 'process_template',
            label: i18n.t('流程模板'),
            min_width: 200
        }, {
            id: 'project',
            label: i18n.t('项目'),
            isShow: true,
            width: 140
        }, {
            id: 'cron',
            label: i18n.t('周期规则'),
            width: 150
        }, {
            id: 'last_run_at',
            label: i18n.t('上次运行时间'),
            width: 200
        }, {
            id: 'creator',
            label: i18n.t('创建人'),
            disabled: true,
            width: 120
        }, {
            id: 'create_time',
            label: i18n.t('创建时间'),
            width: 200
        }, {
            id: 'editor',
            label: i18n.t('更新人'),
            disabled: true,
            width: 120
        }, {
            id: 'edit_time',
            label: i18n.t('更新时间'),
            disabled: true,
            width: 200
        }, {
            id: 'total_run_count',
            label: i18n.t('运行次数'),
            width: 100
        }
    ]
    export default {
        name: 'PeriodicList',
        components: {
            Skeleton,
            SearchSelect,
            NoData,
            TaskCreateDialog,
            ModifyPeriodicDialog,
            BootRecordDialog,
            DeletePeriodicDialog
        },
        mixins: [permission],
        props: {
            project_id: {
                type: [String, Number]
            },
            admin: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const {
                page = 1,
                limit = 15,
                creator = '',
                enabled = '',
                taskName = '',
                editor = '',
                task_id = '',
                last_run_at = '',
                create_time = '',
                edit_time = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'last_run_at', name: i18n.t('上次运行时间'), type: 'dateRange' },
                { id: 'create_time', name: i18n.t('创建时间'), type: 'dateRange' },
                { id: 'edit_time', name: i18n.t('更新时间'), type: 'dateRange' }
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
                businessInfoLoading: true,
                isNewTaskDialogShow: false,
                listLoading: false,
                deleting: false,
                totalPage: 1,
                isDeleteDialogShow: false,
                isModifyDialogShow: false,
                isBootRecordDialogShow: false,
                selectedPeriodicId: undefined,
                periodicList: [],
                collectingId: '', // 正在被收藏/取消收藏的周期任务id
                selectedCron: undefined,
                constants: {},
                modifyDialogLoading: false,
                selectedTemplateName: undefined,
                periodEntrance: '',
                taskCategory: [],
                requestData: {
                    creator,
                    enabled,
                    taskName,
                    editor,
                    task_id,
                    last_run_at: last_run_at ? last_run_at.split(',') : ['', ''],
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    edit_time: edit_time ? edit_time.split(',') : ['', '']
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
                editTask: true, // 编辑/创建周期任务
                curRow: {}, // 当前选中行的数据
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue
            }
        },
        computed: {
            ...mapState({
                username: state => state.username,
                hasAdminPerm: state => state.hasAdminPerm
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone
            }),
            adminView () {
                return this.hasAdminPerm && this.admin
            },
            projectId () {
                return this.adminView ? this.curRow.project.id : this.project_id
            }
        },
        async created () {
            this.getFields()
            this.getBizBaseInfo()
            await this.getPeriodicList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions([
                'addToCollectList',
                'deleteCollect'
            ]),
            ...mapActions('periodic/', [
                'loadPeriodicList',
                'setPeriodicEnable',
                'getPeriodic',
                'deletePeriodic'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            async getPeriodicList () {
                this.listLoading = true
                try {
                    const { creator, enabled, taskName, task_id, editor, last_run_at, create_time, edit_time } = this.requestData
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        task__celery_task__enabled: enabled || undefined,
                        task__creator: creator || undefined,
                        task__name__icontains: taskName || undefined,
                        id: task_id || undefined,
                        editor: editor || undefined
                    }

                    if (last_run_at && last_run_at[0] && last_run_at[1]) {
                        data['task__last_run_at__gte'] = moment.tz(last_run_at[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        data['task__last_run_at__lte'] = moment.tz(last_run_at[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD HH:mm:ss')
                    }
                    if (create_time && create_time[0] && create_time[1]) {
                        data['create_time__gte'] = moment.tz(create_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        data['create_time__lte'] = moment.tz(create_time[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD HH:mm:ss')
                    }
                    if (edit_time && edit_time[0] && edit_time[1]) {
                        data['edit_time__gte'] = moment.tz(edit_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        data['edit_time__lte'] = moment.tz(edit_time[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD HH:mm:ss')
                    }

                    if (!this.admin) {
                        data.project__id = this.project_id
                    }

                    const periodicListData = await this.loadPeriodicList(data)
                    const list = periodicListData.results
                    this.periodicList = list
                    this.pagination.count = periodicListData.count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                }
            },
            async getBizBaseInfo () {
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.taskCategory = res.data.task_categories
                } catch (e) {
                    console.log(e)
                }
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('PeriodicList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields
                    if (!fieldList || !size) {
                        localStorage.removeItem('PeriodicList')
                    }
                } else {
                    selectedFields = this.tableFields.reduce((acc, cur) => {
                        if (cur.id !== 'create_time') { // 默认不显示创建时间
                            acc.push(cur.id)
                        }
                        return acc
                    }, [])
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
            },
            getEditPerm (row) {
                if (row.template_source === 'common') {
                    return ['common_flow_view', 'periodic_task_edit']
                }
                return ['flow_view', 'periodic_task_edit']
            },
            /**
             * 单个周期任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} periodic 模板数据对象
             */
            onPeriodicPermissonCheck (required, periodic) {
                const { id, name, task_template_name, template_id, project, auth_actions, template_source } = periodic
                const isCommon = template_source === 'common'
                const resourceData = {
                    periodic_task: [{ id, name }],
                    [isCommon ? 'common_flow' : 'flow']: [{
                        id: template_id,
                        name: task_template_name
                    }],
                    project: [{
                        id: project.id,
                        name: project.name
                    }]
                }
                this.applyForPermission(required, auth_actions, resourceData)
            },
            onDeletePeriodic (periodic) {
                if (!this.hasPermission(['periodic_task_delete'], periodic.auth_actions)) {
                    this.onPeriodicPermissonCheck(['periodic_task_delete'], periodic)
                    return
                }
                this.isDeleteDialogShow = true
                this.selectedDeleteTaskId = periodic.id
                this.selectedTemplateName = periodic.name
            },
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('PeriodicList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getPeriodicList()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getPeriodicList()
            },
            renderTableHeader (h, { column, $index }) {
                if (['last_run_at', 'create_time', 'edit_time'].includes(column.property)) {
                    const index = this.adminView ? $index : $index + 1
                    const id = this.setting.selectedFields[index].id
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
                            name: id === 'last_run_at' ? i18n.t('上次运行时间') : id === 'create_time' ? i18n.t('创建时间') : i18n.t('更新时间'),
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
                this.getPeriodicList()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { creator, enabled, taskName, task_id, last_run_at, create_time, edit_time } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    enabled,
                    page: current,
                    taskName,
                    task_id,
                    last_run_at: last_run_at && last_run_at.every(item => item) ? last_run_at.join(',') : '',
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    edit_time: edit_time && edit_time.every(item => item) ? edit_time.join(',') : ''
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                if (this.admin) {
                    this.$router.replace({ name: 'adminPeriodic', query })
                } else {
                    this.$router.replace({ name: 'periodicTemplate', params: { project_id: this.project_id }, query })
                }
            },
            async onSetEnable (item) {
                if (!this.hasPermission(['periodic_task_edit'], item.auth_actions)) {
                    this.onPeriodicPermissonCheck(['periodic_task_edit'], item)
                    return
                }
                try {
                    const data = {
                        'taskId': item.id,
                        'enabled': !item.enabled
                    }
                    const periodicData = await this.setPeriodicEnable(data)
                    if (periodicData.result) {
                        const periodic = this.periodicList.find(periodic => periodic.id === item.id)
                        periodic.enabled = !periodic.enabled
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            judgeOldCommonPeriodic (row) {
                return row.is_latest === null && row.template_source === 'common'
            },
            async onModifyCronPeriodic (item) {
                const { id: taskId, cron, is_latest, template_source } = item
                if (!this.hasPermission(this.getEditPerm(item), item.auth_actions)) {
                    this.onPeriodicPermissonCheck(this.getEditPerm(item), item)
                    return
                }
                if (is_latest === null && template_source === 'common') {
                    return
                }
                const splitCron = this.splitPeriodicCron(cron)
                this.selectedCron = splitCron
                this.selectedPeriodicId = taskId
                await this.getPeriodicConstant(taskId)
                this.editTask = true
                this.isModifyDialogShow = true
            },
            onUpdateTask (row) {
                const curRow = this.periodicList.find(item => item.id === row.id)
                curRow.is_latest = true
            },
            onModifyPeriodicCancel () {
                this.curRow = {}
                this.isModifyDialogShow = false
            },
            onModifyPeriodicConfirm () {
                this.curRow = {}
                this.isModifyDialogShow = false
                this.getPeriodicList()
            },
            async getPeriodicConstant (taskId) {
                this.modifyDialogLoading = true
                const data = {
                    'taskId': taskId
                }
                const periodic = await this.getPeriodic(data)
                this.curRow = periodic
                this.constants = periodic.form
                this.modifyDialogLoading = false
            },
            onDeletePeriodicConfirm () {
                this.deleteSelecedPeriodic()
            },
            async deleteSelecedPeriodic () {
                if (this.deleting) {
                    return
                }
                try {
                    this.deleting = true
                    await this.deletePeriodic(this.selectedDeleteTaskId)
                    this.$bkMessage({
                        'message': i18n.t('周期任务') + i18n.t('删除成功'),
                        'theme': 'success'
                    })
                    this.isDeleteDialogShow = false
                    // 最后一页最后一条删除后，往前翻一页
                    if (
                        this.pagination.current > 1
                        && this.totalPage === this.pagination.current
                        && this.pagination.count - (this.totalPage - 1) * this.pagination.limit === 1
                    ) {
                        this.pagination.current -= 1
                    }
                    this.getPeriodicList()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.deleting = false
                }
            },
            onDeletePeriodicCancel () {
                this.isDeleteDialogShow = false
            },
            splitPeriodicCron (cron) {
                return cron.split('(')[0].trim()
            },
            onCreatePeriodTask () {
                this.curRow = {}
                this.constants = {}
                this.editTask = false
                this.isModifyDialogShow = true
            },
            onCreateTaskCancel () {
                this.isNewTaskDialogShow = false
            },
            onRecordView (task) {
                this.selectedPeriodicId = task.id
                this.isBootRecordDialogShow = true
            },
            templateNameUrl (template) {
                const { template_id: templateId, template_source: templateSource, project } = template
                const isCommon = templateSource === 'common'
                const url = {
                    name: isCommon ? 'commonTemplatePanel' : 'templatePanel',
                    params: { type: 'view', project_id: isCommon ? undefined : project.id },
                    query: { template_id: templateId, common: isCommon ? 1 : undefined }
                }
                return url
            },
            // 添加/取消收藏模板
            async onCollectTask (task, event) {
                if (!this.hasPermission(['periodic_task_view'], task.auth_actions)) {
                    this.onPeriodicPermissonCheck(['periodic_task_view'], task, event)
                    return
                }
                if (typeof this.collectingId === 'number') {
                    return
                }

                try {
                    this.collectingId = task.id
                    if (!task.is_collected) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                project_id: task.project.id,
                                project_name: task.project.name,
                                template_id: task.template_id,
                                name: task.name,
                                id: task.id
                            },
                            instance_id: task.id,
                            username: this.username,
                            category: 'periodic_task'
                        }])
                        if (res.data.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                        task.collection_id = res.data[0].id
                    } else { // cancel
                        await this.deleteCollect(task.collection_id)
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                        task.collection_id = 0
                    }
                    task.is_collected = task.is_collected ? 0 : 1
                } catch (e) {
                    console.log(e)
                } finally {
                    this.collectingId = ''
                }
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.periodic-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;
    @include scrollbar;
}
.search-wrapper {
    position: relative;
    height: 32px;
    display: flex;
    justify-content: space-between;
}
.list-wrapper {
    min-height: calc(100vh - 300px);
    .advanced-search {
        margin: 0px;
    }
}
.query-button {
    padding: 10px;
    min-width: 450px;
    @media screen and (max-width: 1420px) {
        min-width: 390px;
    }
    text-align: center;
    .bk-button {
        height: 32px;
        line-height: 32px;
    }
    .query-cancel {
        margin-left: 5px;
    }
}
.periodic-table-content {
    margin-top: 25px;
    background: #ffffff;
    /deep/ .bk-table {
        td.is-last .cell {
            overflow: visible;
        }
    }
    .bk-table-row.hover-row {
        .icon-favorite {
            display: block;
        }
    }
    .icon-favorite {
        position: absolute;
        top: 14px;
        left: -9px;
        font-size: 14px;
        color: #c4c6cc;
        display: none;
        &.is-active {
            display: block;
            color: #ff9c01;
        }
    }
    .task-name {
        display: flex;
        align-items: center;
        .name {
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
        .label {
            flex-shrink: 0;
            width: 44px;
            height: 22px;
            text-align: center;
            line-height: 20px;
            margin-left: 5px;
            background: #fafbfd;
            border: 1px solid rgba(151,155,165,0.30);
            border-radius: 2px;
            cursor: default;
        }
    }
    .template-name {
        display: flex;
        align-items: center;
        .periodic-name {
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
        .common-icon-update {
            color: #ee392f;
            font-size: 14px;
            cursor: pointer;
            &.is-disabled {
                color: #cccccc;
                cursor: not-allowed;
            }
        }
    }
    .icon-check-circle-shape {
        color: #30d878;
    }
    a.periodic-name,
    .periodic-operation>a {
        color: $blueDefault;
        padding: 5px;
        &.periodic-bk-disable {
            color:#cccccc;
            cursor: not-allowed;
        }
        &.clocked-bk-disable {
            color:#cccccc !important;
            cursor: not-allowed;
        }
    }
    .bk-switcher {
        margin-right: 5px;
    }
    .icon-check-circle-shape {
        color: $greenDefault;
    }
    .common-icon-dark-circle-pause {
        color: #ff9c01;
        border-radius: 20px;
        font-size: 12px;
    }
    .drop-icon-ellipsis {
        font-size: 18px;
        vertical-align: -3px;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            background: #dcdee5;
            border-radius: 50%;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
}
</style>
