<template>
    <div class="clocked-container">
        <skeleton :loading="firstLoading" loader="taskList">
            <div class="list-wrapper">
                <div class="search-wrapper mb20">
                    <bk-button
                        v-if="!adminView"
                        ref="childComponent"
                        theme="primary"
                        size="normal"
                        style="min-width: 120px;"
                        data-test-id="clockedList_form_createTask"
                        @click="onCreateClockedTask">
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
                <div class="clocked-table-content" data-test-id="clockedList_table_taskList">
                    <bk-table
                        :data="clockedList"
                        :pagination="pagination"
                        :size="setting.size"
                        @page-change="onPageChange"
                        @page-limit-change="handlePageLimitChange"
                        v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }">
                        <bk-table-column
                            v-for="item in setting.selectedFields"
                            :key="item.id"
                            :label="item.label"
                            :prop="item.id"
                            :width="item.width"
                            :render-header="renderTableHeader"
                            show-overflow-tooltip
                            :min-width="item.min_width">
                            <template slot-scope="{ row }">
                                <!--流程模板-->
                                <div v-if="item.id === 'template_name'">
                                    <a
                                        v-if="!hasPermission(['clocked_task_view'], row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        :title="row.template_name"
                                        @click="onClockedPermissonCheck(['clocked_task_view'], row, $event)">
                                        {{ row.template_name }}
                                    </a>
                                    <router-link
                                        v-else
                                        class="template-name"
                                        target="_blank"
                                        :title="row.template_name"
                                        :to="templateNameUrl(row)">
                                        {{ row.template_name }}
                                    </router-link>
                                </div>
                                <div v-else-if="item.id === 'state'">
                                    {{ row.state === 'not_started' ? $t('未执行') : row.state === 'started' ? $t('已执行') : row.state ? $t('启动失败') : '--' }}
                                </div>
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="row[item.id] || '--'">{{ row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" :width="adminView ? 120 : 230" :fixed="clockedList.length ? 'right' : false">
                            <div class="clocked-operation" slot-scope="props" :clocked-task-name="props.row.name">
                                <template v-if="!adminView">
                                    <a
                                        v-cursor="{ active: !hasPermission(['flow_view', 'clocked_task_edit'], props.row.auth_actions) }"
                                        href="javascript:void(0);"
                                        :class="{
                                            'clocked-bk-disable': props.row.state !== 'not_started',
                                            'text-permission-disable': !hasPermission(['flow_view', 'clocked_task_edit'], props.row.auth_actions)
                                        }"
                                        v-bk-tooltips.top="{
                                            content: props.row.task_id ? $t('已执行的计划任务无法编辑') : $t('启动失败的计划任务无法编辑'),
                                            disabled: !hasPermission(['flow_view', 'clocked_task_edit'], props.row.auth_actions) || props.row.state === 'not_started'
                                        }"
                                        data-test-id="clockedList_table_editBtn"
                                        @click="onEditClockedTask(props.row, $event)">
                                        {{ $t('编辑') }}
                                    </a>
                                    <a
                                        v-cursor="{ active: !hasPermission(['flow_view', 'clocked_task_view'], props.row.auth_actions) }"
                                        href="javascript:void(0);"
                                        :class="{
                                            'clocked-bk-disable': !hasPermission(['flow_view', 'clocked_task_view'], props.row.auth_actions)
                                        }"
                                        data-test-id="clockedList_table_cloneBtn"
                                        @click="onCloneClockedTask(props.row, 'clone')">
                                        {{ $t('克隆') }}
                                    </a>
                                    <a
                                        v-cursor="{ active: !hasPermission(['clocked_task_delete'], props.row.auth_actions) }"
                                        href="javascript:void(0);"
                                        :class="{
                                            'clocked-bk-disable': !hasPermission(['clocked_task_delete'], props.row.auth_actions)
                                        }"
                                        data-test-id="clockedList_table_deleteBtn"
                                        @click="onDeleteClockedTask(props.row, $event)">
                                        {{ $t('删除') }}
                                    </a>
                                </template>
                                <template v-if="props.row.task_id">
                                    <a
                                        v-if="!hasPermission(['clocked_task_view'], props.row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        data-test-id="clockedList_table_executeHistoryBtn"
                                        @click="onClockedPermissonCheck(['clocked_task_view'], props.row, $event)">
                                        {{ $t('执行历史') }}
                                    </a>
                                    <router-link
                                        v-else
                                        class="task-name"
                                        data-test-id="clockedList_table_executeHistoryBtn"
                                        :to="{
                                            name: 'taskExecute',
                                            params: { project_id: props.row.project_id },
                                            query: { instance_id: props.row.task_id }
                                        }">
                                        {{ $t('执行历史') }}
                                    </router-link>
                                </template>
                                <span v-else class="empty-text">{{ '--' }}</span>
                            </div>
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
            :entrance="'clockedTask'"
            :project_id="project_id"
            :is-new-task-dialog-show="isNewTaskDialogShow"
            :business-info-loading="businessInfoLoading"
            :task-category="taskCategory"
            :dialog-title="$t('新建计划任务')"
            @onCreateTaskCancel="onCreateTaskCancel">
        </TaskCreateDialog>
        <EditClockedTask
            v-if="isShowSideslider"
            :is-show-sideslider="isShowSideslider"
            :cur-row="curRow"
            :project_id="projectId"
            :type="sideSliderType"
            @onSaveConfig="onSaveConfig"
            @onCloseConfig="onCloseConfig">
        </EditClockedTask>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import { mapActions, mapState } from 'vuex'
    import moment from 'moment-timezone'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskCreateDialog from '../../task/TaskList/TaskCreateDialog.vue'
    import EditClockedTask from './EditClockedTask.vue'
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
            id: 'creator',
            name: i18n.t('创建人')
        },
        {
            id: 'editor',
            name: i18n.t('更新人')
        },
        {
            id: 'state',
            name: i18n.t('状态'),
            children: [
                { id: 'not_started', name: i18n.t('未执行') },
                { id: 'started', name: i18n.t('已执行') },
                { id: 'start_failed', name: i18n.t('启动失败') }
            ]
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
            width: 80
        }, {
            id: 'task_name',
            label: i18n.t('计划任务'),
            min_width: 200
        }, {
            id: 'template_name',
            label: i18n.t('流程模板'),
            min_width: 200
        }, {
            id: 'plan_start_time',
            label: i18n.t('启动时间'),
            width: 200
        }, {
            id: 'creator',
            label: i18n.t('创建人'),
            disabled: true,
            width: 150
        }, {
            id: 'editor',
            label: i18n.t('更新人'),
            disabled: true,
            width: 150
        }, {
            id: 'create_time',
            label: i18n.t('创建时间'),
            width: 200
        }, {
            id: 'edit_time',
            label: i18n.t('更新时间'),
            disabled: true,
            width: 200
        }, {
            id: 'state',
            label: i18n.t('任务状态'),
            width: 150
        }
    ]
    export default {
        name: 'ClockedList',
        components: {
            Skeleton,
            NoData,
            SearchSelect,
            TaskCreateDialog,
            EditClockedTask
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
                editor = '',
                plan_start_time = '',
                create_time = '',
                edit_time = '',
                taskName = '',
                task_id = '',
                state = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'plan_start_time', name: i18n.t('启动时间'), type: 'dateRange' },
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
                clockedList: [],
                listLoading: false,
                requestData: {
                    creator,
                    editor,
                    plan_start_time: plan_start_time ? plan_start_time.split(',') : ['', ''],
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    edit_time: edit_time ? edit_time.split(',') : ['', ''],
                    taskName,
                    task_id,
                    state
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
                isNewTaskDialogShow: false,
                taskCategory: [],
                businessInfoLoading: true,
                deleting: false,
                curRow: {},
                sideSliderType: '',
                isShowSideslider: false,
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue
            }
        },
        computed: {
            ...mapState({
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
            await this.getClockedTaskList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('project', [
                'loadProjectDetail'
            ]),
            ...mapActions('clocked/', [
                'loadClockedList',
                'deleteClocked',
                'getClockedDetail'
            ]),
            // 获取计划任务列表
            async getClockedTaskList () {
                try {
                    this.listLoading = true
                    const { creator, plan_start_time, create_time, edit_time, taskName, task_id, editor, state } = this.requestData
                    const params = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        creator: creator || undefined,
                        task_name__icontains: taskName || undefined,
                        id: task_id || undefined,
                        editor: editor || undefined,
                        state: state || undefined
                    }
                    if (!this.admin) {
                        params.project_id = this.project_id
                    }
                    if (plan_start_time && plan_start_time[0] && plan_start_time[1]) {
                        params['plan_start_time__gte'] = moment.tz(plan_start_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        params['plan_start_time__lte'] = moment.tz(plan_start_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    }
                    if (create_time && create_time[0] && create_time[1]) {
                        params['create_time__gte'] = moment.tz(create_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        params['create_time__lte'] = moment.tz(create_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    }
                    if (edit_time && edit_time[0] && edit_time[1]) {
                        params['edit_time__gte'] = moment.tz(edit_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                        params['edit_time__lte'] = moment.tz(edit_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    }
                    const source = new CancelRequest()
                    const resp = await this.loadClockedList({
                        params,
                        config: { cancelToken: source.token }
                    })
                    this.pagination.count = resp.data.count
                    this.clockedList = resp.data.results
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.listLoading = false
                }
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('ClockedList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields
                    if (!fieldList || !size) {
                        localStorage.removeItem('ClockedList')
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
            // 获取业务类别
            async getBizBaseInfo () {
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.taskCategory = res.data.task_categories
                } catch (e) {
                    console.log(e)
                }
            },
            // 创建计划任务
            onCreateClockedTask () {
                this.curRow = {}
                this.sideSliderType = 'create'
                this.isShowSideslider = true
            },
            // 取消创建
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
                this.requestData = data
                this.pagination.current = 1
                this.updateUrl()
                this.getClockedTaskList()
            },
            // 页数改变
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getClockedTaskList()
            },
            // 页码改变
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getClockedTaskList()
            },
            renderTableHeader (h, { column, $index }) {
                if (['plan_start_time', 'create_time', 'edit_time'].includes(column.property)) {
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
                            name: id === 'plan_start_time' ? i18n.t('启动时间') : id === 'create_time' ? i18n.t('创建时间') : i18n.t('更新时间'),
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
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('ClockedList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            // 更新路径
            updateUrl () {
                const { current, limit } = this.pagination
                const { creator, plan_start_time, create_time, edit_time, taskName, task_id, state, editor } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    plan_start_time: plan_start_time && plan_start_time.every(item => item) ? plan_start_time.join(',') : '',
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    edit_time: edit_time && edit_time.every(item => item) ? edit_time.join(',') : '',
                    page: current,
                    taskName,
                    task_id,
                    state,
                    editor
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                if (this.admin) {
                    this.$router.replace({ name: 'adminClocked', query })
                } else {
                    this.$router.replace({ name: 'clockedTemplate', params: { project_id: this.project_id }, query })
                }
            },
            // 获取前往对应模板的路径
            templateNameUrl (row) {
                const { template_id, project_id } = row
                const url = {
                    name: 'templatePanel',
                    params: { type: 'view', project_id },
                    query: { template_id, common: undefined }
                }
                return url
            },
            /**
             * 单个计划任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} clocked 模板数据对象
             */
            async onClockedPermissonCheck (required, row) {
                const { id, task_name, template_name, template_id, project_id } = row
                const projectDetail = await this.loadProjectDetail(project_id)
                const resourceData = {
                    clocked_task: [{ id, name: task_name }],
                    flow: [{
                        id: template_id,
                        name: template_name
                    }],
                    project: [{
                        id: project_id,
                        name: projectDetail.name
                    }]
                }
                this.applyForPermission(required, row.auth_actions, resourceData)
            },
            // 编辑计划任务
            async onEditClockedTask (row) {
                // 已执行的计划任务禁止编辑
                if (row.task_id) return
                // 权限校验
                if (!this.hasPermission(['flow_view', 'clocked_task_edit'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['flow_view', 'clocked_task_edit'], row)
                    return
                }
                // 已执行的计划任务禁止编辑
                if (row.state !== 'not_started') return
                // 检查计划任务是否已执行
                const resp = await this.getClockedDetail(row)
                if (resp.data.task_id) {
                    this.$bkMessage({
                        'message': i18n.t('该计划任务已执行，请重新创建'),
                        'theme': 'warning '
                    })
                    const index = this.clockedList.findIndex(item => item.id === row.id)
                    this.clockedList.splice(index, 1, resp.data)
                    return
                }
                this.curRow = row
                this.sideSliderType = 'edit'
                this.isShowSideslider = true
            },
            // 克隆计划任务
            onCloneClockedTask (row) {
                if (!this.hasPermission(['flow_view', 'clocked_task_view'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['flow_view', 'clocked_task_view'], row)
                    return
                }
                this.curRow = row
                this.sideSliderType = 'clone'
                this.isShowSideslider = true
            },
            // 保存编辑计划任务
            onSaveConfig () {
                this.getClockedTaskList()
                this.onCloseConfig()
            },
            // 取消编辑计划任务
            onCloseConfig () {
                this.isShowSideslider = false
                this.curRow = {}
            },
            // 删除计划任务
            onDeleteClockedTask (row) {
                if (!this.hasPermission(['clocked_task_delete'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['clocked_task_delete'], row)
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
                        }, [i18n.t('确认删除') + i18n.t('计划任务') + '"' + row.task_name + '"?'])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.onDeleteClockedConfirm(row.id)
                    }
                })
            },
            // 同意删除计划任务
            async onDeleteClockedConfirm (taskId) {
                if (this.deleting) return
                try {
                    this.deleting = true
                    await this.deleteClocked({ id: taskId })
                    this.$bkMessage({
                        'message': i18n.t('计划任务删除成功'),
                        'theme': 'success'
                    })
                    // 最后一页最后一条删除后，往前翻一页
                    if (this.pagination.current > 1 && this.clockedList.length === 1) {
                        this.pagination.current -= 1
                        this.updateUrl()
                    }
                    this.getClockedTaskList()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.deleting = false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.clocked-container {
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
.clocked-table-content {
    margin-top: 25px;
    background: #ffffff;
    /deep/ .bk-table {
        td.is-last .cell {
            overflow: visible;
        }
    }
    .template-name,
    .task-name,
    .clocked-operation > a {
        color: $blueDefault;
        padding: 5px;
        cursor: pointer;
        &.clocked-bk-disable {
            color:#cccccc !important;
            cursor: not-allowed;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
    .empty-text {
        padding: 5px;
    }
}
</style>
