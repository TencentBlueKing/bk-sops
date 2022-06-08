<template>
    <div class="clocked-container">
        <skeleton :loading="firstLoading" loader="taskList">
            <div class="list-wrapper">
                <advance-search-form
                    id="clockedList"
                    :open="isSearchFormOpen"
                    :search-config="{ placeholder: $t('请输入任务名称'), value: requestData.taskName }"
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-if="!adminView" v-slot:operation>
                        <bk-button
                            ref="childComponent"
                            theme="primary"
                            size="normal"
                            style="min-width: 120px;"
                            data-test-id="clockedList_form_createTask"
                            @click="onCreateClockedTask">
                            {{$t('新建')}}
                        </bk-button>
                    </template>
                </advance-search-form>
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
                                <!--任务实例-->
                                <div v-else-if="item.id === 'task_instance'">
                                    <template v-if="row.task_id">
                                        <a
                                            v-if="!hasPermission(['clocked_task_view'], row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            :title="row.task_name"
                                            @click="onClockedPermissonCheck(['clocked_task_view'], row, $event)">
                                            {{ row.task_name }}
                                        </a>
                                        <router-link
                                            v-else
                                            class="task-name"
                                            target="_blank"
                                            :title="row.task_name"
                                            :to="{
                                                name: 'taskExecute',
                                                params: { project_id: row.project_id },
                                                query: { instance_id: row.task_id }
                                            }">
                                            {{ row.task_name }}
                                        </router-link>
                                    </template>
                                    <template v-else>{{ '--' }}</template>
                                </div>
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="row[item.id] || '--'">{{ row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="240">
                            <div class="clocked-operation" slot-scope="props">
                                <a
                                    v-cursor="{ active: !hasPermission(['clocked_task_edit'], props.row.auth_actions) }"
                                    href="javascript:void(0);"
                                    :class="{
                                        'clocked-bk-disable': !hasPermission(['clocked_task_edit'], props.row.auth_actions) || props.row.task_id
                                    }"
                                    v-bk-tooltips.top="{
                                        content: $t('已执行的计划任务无法编辑'),
                                        disabled: hasPermission(['clocked_task_edit'], props.row.auth_actions) ? !props.row.task_id : true
                                    }"
                                    data-test-id="clockedList_table_editBtn"
                                    @click="onEditClockedTask(props.row, $event)">
                                    {{ $t('编辑') }}
                                </a>
                                <a
                                    v-cursor="{ active: !hasPermission(['clocked_task_view'], props.row.auth_actions) }"
                                    href="javascript:void(0);"
                                    :class="{
                                        'clocked-bk-disable': !hasPermission(['clocked_task_view'], props.row.auth_actions)
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
                        <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
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
            :project_id="project_id"
            :type="sideSliderType"
            @onSaveConfig="onSaveConfig"
            @onCloseConfig="onCloseConfig">
        </EditClockedTask>
        <DeleteClockedDialog
            :is-delete-dialog-show="isDeleteDialogShow"
            :template-name="selectedTemplateName"
            :deleting="deleting"
            @onDeleteClockedConfirm="onDeleteClockedConfirm"
            @onDeleteClockedCancel="onDeleteClockedCancel">
        </DeleteClockedDialog>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import { mapActions, mapState } from 'vuex'
    import moment from 'moment-timezone'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskCreateDialog from '../../task/TaskList/TaskCreateDialog.vue'
    import EditClockedTask from './EditClockedTask.vue'
    import DeleteClockedDialog from './DeleteClockedDialog.vue'
    const SEARCH_FORM = [
        {
            type: 'input',
            key: 'creator',
            label: i18n.t('创建人'),
            placeholder: i18n.t('请输入创建人'),
            value: ''
        },
        {
            type: 'dateRange',
            key: 'executeTime',
            label: i18n.t('启动时间'),
            placeholder: i18n.t('如：2019-01-30 至 2019-02-30'),
            value: ['', '']
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
            id: 'task_instance',
            label: i18n.t('任务实例'),
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
        }
    ]
    export default {
        name: 'ClockedList',
        components: {
            Skeleton,
            AdvanceSearchForm,
            NoData,
            TaskCreateDialog,
            EditClockedTask,
            DeleteClockedDialog
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
            const { page = 1, limit = 15, creator = '', executeTime = '', keyword = '' } = this.$route.query
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
                clockedList: [],
                listLoading: false,
                isSearchFormOpen,
                searchForm,
                requestData: {
                    creator,
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
                },
                isNewTaskDialogShow: false,
                taskCategory: [],
                businessInfoLoading: true,
                isDeleteDialogShow: false,
                selectedDeleteTaskId: 0,
                selectedTemplateName: '',
                deleting: false,
                curRow: {},
                sideSliderType: '',
                isShowSideslider: false
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
            }
        },
        async created () {
            this.getFields()
            this.getBizBaseInfo()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
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
                    const { creator, executeTime, taskName } = this.requestData
                    const params = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        creator: creator || undefined,
                        task_name__contains: taskName || undefined
                    }
                    if (!this.admin) {
                        params.project_id = this.project_id
                    }
                    if (executeTime[0] && executeTime[1]) {
                        params['plan_start_time__gte'] = moment.tz(executeTime[0], this.timeZone).format('YYYY-MM-DD hh:mm:ss')
                        params['plan_start_time__lte'] = moment.tz(executeTime[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD hh:mm:ss')
                    }
                    const resp = await this.loadClockedList(params)
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
            searchInputhandler (data) {
                this.requestData.taskName = data
                this.pagination.current = 1
                this.updateUrl()
                this.getClockedTaskList()
            },
            // 高级搜索提交
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
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
                const { creator, executeTime, taskName } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    executeTime: executeTime.every(item => item) ? executeTime.join(',') : '',
                    page: current,
                    keyword: taskName
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.replace({ name: 'clockedTemplate', params: { project_id: this.project_id }, query })
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
                // 权限校验
                if (!this.hasPermission(['clocked_task_edit'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['clocked_task_edit'], row)
                    return
                }
                if (row.task_id) return
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
                if (!this.hasPermission(['clocked_task_view'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['clocked_task_view'], row)
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
                this.isDeleteDialogShow = true
                this.selectedDeleteTaskId = row.id
                this.selectedTemplateName = row.task_name
            },
            // 同意删除计划任务
            async onDeleteClockedConfirm () {
                if (this.deleting) return
                try {
                    this.deleting = true
                    await this.deleteClocked({ id: this.selectedDeleteTaskId })
                    this.$bkMessage({
                        'message': i18n.t('删除计划任务成功'),
                        'theme': 'success'
                    })
                    this.isDeleteDialogShow = false
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
            },
            // 取消删除计划任务
            onDeleteClockedCancel () {
                this.isDeleteDialogShow = false
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
            color:#cccccc;
            cursor: not-allowed;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
}
</style>
