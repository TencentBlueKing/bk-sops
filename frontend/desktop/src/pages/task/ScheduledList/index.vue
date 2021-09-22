<template>
    <div class="scheduled-container">
        <skeleton :loading="firstLoading" loader="taskList">
            <div class="list-wrapper">
                <advance-search-form
                    id="periodicList"
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
                            @click="onCreateScheduledTask">
                            {{$t('新建')}}
                        </bk-button>
                    </template>
                </advance-search-form>
                <div class="scheduled-table-content">
                    <bk-table
                        :data="scheduledList"
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
                                    <!-- <a
                                        v-if="!hasPermission(['scheduled_task_view'], row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['scheduled_task_view'], row, $event)">
                                        {{ row.task_template_name }}
                                    </a> -->
                                    <router-link
                                        class="template-name"
                                        :title="row.task_template_name"
                                        :to="templateNameUrl(row)">
                                        {{ row.task_template_name }}
                                    </router-link>
                                </div>
                                <!--任务实例-->
                                <div v-else-if="item.id === 'task_instance'">
                                    <span
                                        class="task-instance"
                                        @click="onScheduledPermissonCheck(['scheduled_task_view'], row, $event)">
                                        {{ row[item.id] || '--' }}
                                    </span>
                                </div>
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="row[item.id] || '--'">{{ row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="240">
                            <div class="scheduled-operation" slot-scope="props">
                                <a
                                    v-cursor="{ active: !hasPermission(['scheduled_task_edit'], props.row.auth_actions) }"
                                    href="javascript:void(0);"
                                    :class="['scheduled-bk-btn', {
                                        'scheduled-bk-disable': props.row.enabled,
                                        'text-permission-disable': !hasPermission(['scheduled_task_edit'], props.row.auth_actions)
                                    }]"
                                    @click="onEditScheduled(props.row, $event)">
                                    {{ $t('编辑') }}
                                </a>
                                <a
                                    v-cursor="{ active: !hasPermission(['scheduled_task_delete'], props.row.auth_actions) }"
                                    href="javascript:void(0);"
                                    :class="{
                                        'text-permission-disable': !hasPermission(['scheduled_task_delete'], props.row.auth_actions)
                                    }"
                                    @click="onDeleteScheduled(props.row, $event)">
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
        <EditScheduled
            :is-show-sideslider="isShowSideslider"
            title="编辑计划任务"
            @onSaveConfig="onSaveConfig"
            @onCloseConfig="onCloseConfig">
        </EditScheduled>
        <DeleteScheduledDialog
            :is-delete-dialog-show="isDeleteDialogShow"
            :template-name="selectedTemplateName"
            :deleting="deleting"
            @onDeletePeriodicConfirm="onDeleteScheduledConfirm"
            @onDeletePeriodicCancel="onDeleteScheduledCancel">
        </DeleteScheduledDialog>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import { mapActions, mapState } from 'vuex'
    import EditScheduled from './EditScheduled.vue'
    import DeleteScheduledDialog from './DeleteScheduledDialog.vue'
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
            id: 'scheduled_task',
            label: i18n.t('任务计划'),
            min_width: 200
        }, {
            id: 'process_template',
            label: i18n.t('流程模板'),
            min_width: 200
        }, {
            id: 'task_instance',
            label: i18n.t('任务实例'),
            width: 200
        }, {
            id: 'start_time',
            label: i18n.t('启动时间'),
            width: 200
        }, {
            id: 'creator',
            label: i18n.t('创建人'),
            width: 150
        }
    ]
    export default {
        name: 'ScheduledList',
        components: {
            Skeleton,
            AdvanceSearchForm,
            EditScheduled,
            DeleteScheduledDialog
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
                scheduledList: [
                    {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 57,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
                    }, {
                        task_template_name: '我是计划名称2',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划名称2',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划名称2',
                        process_template: '我是计划名称2'
                    }, {
                        task_template_name: '国庆加班大礼包',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '国庆加班大礼包',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '国庆加班大礼包',
                        process_template: '国庆加班大礼包'
                    }, {
                        task_template_name: '我是计划任务名称',
                        auth_actions: [],
                        id: 1,
                        scheduled_task: '我是计划任务名称',
                        creator: 'admin',
                        start_time: '2021-09-22 14:40:31',
                        task_instance: '我是计划任务名称',
                        process_template: '我是计划任务名称'
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
                isDeleteDialogShow: false,
                selectedTemplateName: '',
                deleting: false,
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
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([]),
            // 获取计划任务列表
            getScheduledList () {},
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('ScheduledList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields
                    if (!selectedFields || !size) {
                        localStorage.removeItem('ScheduledList').map(item => item.id)
                    }
                } else {
                    selectedFields = this.tableFields.map(item => item.id)
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
            },
            // 创建计划任务
            onCreateScheduledTask () {},
            // 高级搜索提交
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
                this.pagination.current = 1
            },
            // 页数改变
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getScheduledList()
            },
            // 页码改变
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getScheduledList()
            },
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('ScheduledList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            // 更新路径
            updateUrl () {
                const { current, limit } = this.pagination
                const { creator, enabled, taskName } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    enabled,
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
                if (this.admin) {
                    this.$router.replace({ name: 'adminPeriodic', query })
                } else {
                    this.$router.replace({ name: 'periodicTemplate', params: { project_id: this.project_id }, query })
                }
            },
            // 前往对应模板
            onTemplatePermissonCheck () {},
            // 获取前往对应模板的路径
            templateNameUrl (template) {
                // const { template_id: templateId, template_source: templateSource, project } = template
                // const url = {
                //     name: 'templatePanel',
                //     params: { type: 'edit', project_id: project.id },
                //     query: { template_id: templateId, common: templateSource === 'common' || undefined }
                // }
                return ''
            },
            /**
             * 单个计划任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} periodic 模板数据对象
             */
            onScheduledPermissonCheck (required, periodic) {
                const { id, name, task_template_name, template_id, project } = periodic
                const resourceData = {
                    periodic_task: [{ id, name }],
                    flow: [{
                        id: template_id,
                        name: task_template_name
                    }],
                    project: [{
                        id: project.id,
                        name: project.name
                    }]
                }
                this.applyForPermission(required, periodic.auth_actions, resourceData)
            },
            // 编辑计划任务
            onEditScheduled (scheduled) {
                if (!this.hasPermission(['periodic_task_edit'], scheduled.auth_actions)) {
                    this.onScheduledPermissonCheck(['periodic_task_edit'], scheduled)
                    return
                }
                this.isShowSideslider = true
            },
            // 保存编辑计划任务
            onSaveConfig () {},
            // 取消编辑计划任务
            onCloseConfig () {
                this.isShowSideslider = false
            },
            // 删除计划任务
            onDeleteScheduled (scheduled) {
                if (!this.hasPermission(['periodic_task_delete'], scheduled.auth_actions)) {
                    this.onScheduledPermissonCheck(['periodic_task_delete'], scheduled)
                    return
                }
                this.isDeleteDialogShow = true
                this.selectedDeleteTaskId = scheduled.id
                this.selectedTemplateName = scheduled.name
            },
            // 同意删除计划任务
            async onDeleteScheduledConfirm () {
                if (this.deleting) {
                    return
                }
                try {
                    this.deleting = true
                    // await this.deletePeriodic(this.selectedDeleteTaskId)
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
                    this.getScheduledList()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.deleting = false
                }
            },
            // 取消删除计划任务
            onDeleteScheduledCancel () {
                this.isDeleteDialogShow = false
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.scheduled-container {
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
.scheduled-table-content {
    margin-top: 25px;
    background: #ffffff;
    /deep/ .bk-table {
        td.is-last .cell {
            overflow: visible;
        }
    }
    a.template-name,
    .task-instance,
    .scheduled-operation > a {
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
