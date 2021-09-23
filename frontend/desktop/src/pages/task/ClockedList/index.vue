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
                            @click="onCreateClockedTask">
                            {{$t('新建')}}
                        </bk-button>
                    </template>
                </advance-search-form>
                <div class="clocked-table-content">
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
                                <div v-if="item.id === 'process_template'">
                                    <a
                                        v-if="!hasPermission(['clocked_template_view'], row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        :title="row.task_template_name"
                                        @click="onClockedPermissonCheck(['clocked_template_view'], row, $event)">
                                        {{ row.task_template_name }}
                                    </a>
                                    <router-link
                                        v-else
                                        class="template-name"
                                        :title="row.task_template_name"
                                        :to="templateNameUrl(row)">
                                        {{ row.task_template_name }}
                                    </router-link>
                                </div>
                                <!--任务实例-->
                                <div v-else-if="item.id === 'task_instance'">
                                    <template v-if="item.task_id">
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
                                    :class="['clocked-bk-btn', {
                                        'clocked-bk-disable': !props.row.task_id,
                                        'text-permission-disable': !hasPermission(['clocked_task_edit'], props.row.auth_actions)
                                    }]"
                                    @click="onEditClockedTask(props.row, $event)">
                                    {{ $t('编辑') }}
                                </a>
                                <a
                                    v-cursor="{ active: !hasPermission(['clocked_task_delete'], props.row.auth_actions) }"
                                    href="javascript:void(0);"
                                    :class="{
                                        'text-permission-disable': !hasPermission(['clocked_task_delete'], props.row.auth_actions)
                                    }"
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
            :is-show-sideslider="isShowSideslider"
            :cur-row="curRow"
            :title="$t('编辑计划任务')"
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
            key: 'startTime',
            label: i18n.t('启动时间'),
            placeholder: i18n.t('如：2019-01-30 至 2019-01-30'),
            value: ''
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
            width: 200
        }, {
            id: 'plan_start_time',
            label: i18n.t('启动时间'),
            width: 200
        }, {
            id: 'creator',
            label: i18n.t('创建人'),
            width: 150
        }
    ]
    export default {
        name: 'ClockedList',
        components: {
            Skeleton,
            AdvanceSearchForm,
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
            const { page = 1, limit = 15, creator = '', startTime = '', keyword = '' } = this.$route.query
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
                firstLoading: false,
                clockedList: [
                    {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划名称2',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        task_name: '国庆加班大礼包',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        task_name: '我是计划任务名称',
                        creator: 'admin',
                        plan_start_time: '2021-09-22 14:40:31',
                        template_name: '我是计划任务名称'
                    }
                ],
                listLoading: false,
                isSearchFormOpen,
                searchForm,
                requestData: {
                    creator,
                    startTime,
                    taskName: keyword
                },
                pagination: {
                    current: Number(page),
                    count: 100,
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
                selectedTemplateName: '',
                deleting: false,
                curRow: {},
                isShowSideslider: false
            }
        },
        computed: {
            ...mapState({
                hasAdminPerm: state => state.hasAdminPerm
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
        },
        methods: {
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            // 获取计划任务列表
            getClockedTaskList () {},
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('ClockededList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields
                    if (!selectedFields || !size) {
                        localStorage.removeItem('ClockededList').map(item => item.id)
                    }
                } else {
                    selectedFields = this.tableFields.map(item => item.id)
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
                this.isNewTaskDialogShow = true
            },
            // 取消创建
            onCreateTaskCancel () {
                this.isNewTaskDialogShow = false
            },
            // 高级搜索提交
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
                this.pagination.current = 1
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
                localStorage.setItem('ClockededList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            // 更新路径
            updateUrl () {
                const { current, limit } = this.pagination
                const { creator, startTime, taskName } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    startTime,
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
                const { template_id: templateId, template_source: templateSource, project_id } = row
                const url = {
                    name: 'templatePanel',
                    params: { type: 'edit', project_id: project_id },
                    query: { template_id: templateId, common: templateSource === 'common' || undefined }
                }
                return url
            },
            /**
             * 单个计划任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} clocked 模板数据对象
             */
            onClockedPermissonCheck (required, row) {
                const { id, name, task_template_name, template_id, project } = row
                const resourceData = {
                    clocked_task: [{ id, name }],
                    flow: [{
                        id: template_id,
                        name: task_template_name
                    }],
                    project: [{
                        id: project.id,
                        name: project.name
                    }]
                }
                this.applyForPermission(required, row.auth_actions, resourceData)
            },
            // 编辑计划任务
            onEditClockedTask (row) {
                if (!this.hasPermission(['clocked_task_edit'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['clocked_task_edit'], row)
                    return
                }
                this.curRow = row
                this.isShowSideslider = true
            },
            // 保存编辑计划任务
            onSaveConfig () {},
            // 取消编辑计划任务
            onCloseConfig () {
                this.isShowSideslider = false
            },
            // 删除计划任务
            onDeleteClockedTask (row) {
                if (!this.hasPermission(['clocked_task_delete'], row.auth_actions)) {
                    this.onClockedPermissonCheck(['clocked_task_delete'], row)
                    return
                }
                this.isDeleteDialogShow = true
                this.selectedDeleteTaskId = row.id
                this.selectedTemplateName = row.name
            },
            // 同意删除计划任务
            async onDeleteClockedConfirm () {
                if (this.deleting) return
                try {
                    this.deleting = true
                    this.$bkMessage({
                        'message': i18n.t('删除计划任务成功'),
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
    .task-name
    .clocked-operation > a {
        color: $blueDefault;
        padding: 5px;
        cursor: pointer;
        &.template-bk-disable {
            color:#cccccc;
            cursor: not-allowed;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
}
</style>
