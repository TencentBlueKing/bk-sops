/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="periodic-container">
        <div class="list-wrapper">
            <div class="operation-area">
                <advance-search-form
                    :search-config="{ placeholder: i18n.periodicNamePlaceholder, value: requestData.flowName }"
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            ref="childComponent"
                            theme="primary"
                            class="task-create-btn"
                            size="normal"
                            @click="onCreatePeriodTask">
                            {{i18n.createPeriodTask}}
                        </bk-button>
                    </template>
                </advance-search-form>
            </div>
            <div class="periodic-table-content">
                <bk-table
                    :data="periodicList"
                    :pagination="pagination"
                    @page-change="onPageChange"
                    @page-limit-change="handlePageLimitChange"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="i18n.periodicName" prop="name" min-width="200">
                        <template slot-scope="props">
                            <span :title="props.row.name">{{props.row.name}}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.periodicTemplate" min-width="200">
                        <template slot-scope="props">
                            <a
                                v-if="!hasPermission(['view'], props.row.auth_actions, periodicOperations)"
                                v-cursor
                                class="text-permission-disable"
                                @click="onPeriodicPermissonCheck(['view'], props.row, $event)">
                                {{props.row.task_template_name}}
                            </a>
                            <router-link
                                v-else
                                class="periodic-name"
                                :title="props.row.task_template_name"
                                :to="templateNameUrl(props.row.template_id, props.row.template_source)">
                                {{props.row.task_template_name}}
                            </router-link>
                        </template>
                    </bk-table-column>
                    <bk-table-column v-if="adminView" :label="i18n.project" width="140">
                        <template slot-scope="props">
                            <span :title="props.row.project.name">{{ props.row.project.name }}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.periodicRule" width="150">
                        <template slot-scope="props">
                            <div :title="splitPeriodicCron(props.row.cron)">{{ splitPeriodicCron(props.row.cron) }}</div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.lastRunAt" width="200">
                        <template slot-scope="props">
                            <div>{{ props.row.last_run_at || '--' }}</div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator" width="120"></bk-table-column>
                    <bk-table-column :label="i18n.totalRunCount" prop="total_run_count" width="100"></bk-table-column>
                    <bk-table-column :label="i18n.enabled" width="100">
                        <template slot-scope="props" class="periodic-status">
                            <span :class="props.row.enabled ? 'bk-icon icon-check-circle-shape' : 'common-icon-dark-circle-pause'"></span>
                            {{props.row.enabled ? i18n.start : i18n.pause}}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.operation" width="240">
                        <template slot-scope="props">
                            <div class="periodic-operation">
                                <template v-if="!adminView">
                                    <a
                                        v-cursor="{ active: !hasPermission(['edit'], props.row.auth_actions, periodicOperations) }"
                                        href="javascript:void(0);"
                                        :class="['periodic-pause-btn', {
                                            'periodic-start-btn': !props.row.enabled,
                                            'text-permission-disable': !hasPermission(['edit'], props.row.auth_actions, periodicOperations)
                                        }]"
                                        @click="onSetEnable(props.row, $event)">
                                        {{!props.row.enabled ? i18n.start : i18n.pause}}
                                    </a>
                                    <a
                                        v-cursor="{ active: !hasPermission(['edit'], props.row.auth_actions, periodicOperations) }"
                                        href="javascript:void(0);"
                                        :class="['periodic-bk-btn', {
                                            'periodic-bk-disable': props.row.enabled,
                                            'text-permission-disable': !hasPermission(['edit'], props.row.auth_actions, periodicOperations)
                                        }]"
                                        :title="props.row.enabled ? i18n.editTitle : ''"
                                        @click="onModifyCronPeriodic(props.row, $event)">
                                        {{ i18n.edit }}
                                    </a>
                                </template>
                                <a
                                    v-else
                                    href="javascript:void(0);"
                                    @click="onRecordView(props.row, $event)">
                                    {{ i18n.bootRecord }}
                                </a>
                                <router-link
                                    :to="{
                                        name: 'taskList',
                                        params: { project_id: project_id },
                                        query: { template_id: props.row.template_id, create_method: 'periodic' }
                                    }">
                                    {{ i18n.executeHistory }}
                                </router-link>
                                <bk-popover
                                    theme="light"
                                    placement="right-top"
                                    ext-cls="common-dropdown-btn-popver"
                                    :z-index="2000"
                                    :distance="0"
                                    :arrow="false"
                                    :tippy-options="{ boundary: 'window', duration: [0, 0] }">
                                    <i class="bk-icon icon-more drop-icon-ellipsis"></i>
                                    <ul slot="content">
                                        <li class="opt-btn">
                                            <a
                                                v-cursor="{ active: !hasPermission(['view'], props.row.auth_actions, periodicOperations) }"
                                                href="javascript:void(0);"
                                                :class="{
                                                    'text-permission-disable': !hasPermission(['view'], props.row.auth_actions, periodicOperations)
                                                }"
                                                @click="onCollectTask(props.row, $event)">
                                                {{ isCollected(props.row.id) ? i18n.cancelCollection : i18n.collect }}
                                            </a>
                                        </li>
                                        <li class="opt-btn">
                                            <a
                                                v-cursor="{ active: !hasPermission(['delete'], props.row.auth_actions, periodicOperations) }"
                                                href="javascript:void(0);"
                                                :class="{
                                                    'text-permission-disable': !hasPermission(['delete'], props.row.auth_actions, periodicOperations)
                                                }"
                                                @click="onDeletePeriodic(props.row, $event)">
                                                {{ i18n.delete }}
                                            </a>
                                        </li>
                                    </ul>
                                </bk-popover>
                            </div>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="i18n.empty" /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <TaskCreateDialog
            :entrance="'periodicTask'"
            :project_id="project_id"
            :is-new-task-dialog-show="isNewTaskDialogShow"
            :business-info-loading="businessInfoLoading"
            :task-category="taskCategory"
            :dialog-title="i18n.dialogTitle"
            @onCreateTaskCancel="onCreateTaskCancel">
        </TaskCreateDialog>
        <ModifyPeriodicDialog
            :loading="modifyDialogLoading"
            :constants="constants"
            :cron="selectedCron"
            :task-id="selectedPeriodicId"
            :is-modify-dialog-show="isModifyDialogShow"
            @onModifyPeriodicConfirm="onModifyPeriodicConfirm"
            @onModifyPeriodicCancel="onModifyPeriodicCancel">
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
    import '@/utils/i18n.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskCreateDialog from '../../task/TaskList/TaskCreateDialog.vue'
    import ModifyPeriodicDialog from './ModifyPeriodicDialog.vue'
    import BootRecordDialog from './BootRecordDialog.vue'
    import DeletePeriodicDialog from './DeletePeriodicDialog.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    const searchForm = [
        {
            type: 'input',
            key: 'creator',
            label: gettext('创建人'),
            placeholder: gettext('请输入创建人'),
            value: ''
        },
        {
            type: 'select',
            label: gettext('状态'),
            key: 'enabled',
            loading: false,
            placeholder: gettext('请选择状态'),
            list: [
                { 'value': 'true', 'name': gettext('启动') },
                { 'value': 'false', 'name': gettext('暂停') }
            ]
        }
    ]
    export default {
        name: 'PeriodicList',
        components: {
            CopyrightFooter,
            AdvanceSearchForm,
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
            return {
                i18n: {
                    createPeriodTask: gettext('新建'),
                    dialogTitle: gettext('新建周期任务'),
                    lastRunAt: gettext('上次运行时间'),
                    project: gettext('项目'),
                    periodicRule: gettext('周期规则'),
                    periodicTask: gettext('周期任务'),
                    advanceSearch: gettext('高级搜索'),
                    creator: gettext('创建人'),
                    operation: gettext('操作'),
                    start: gettext('启动'),
                    delete: gettext('删除'),
                    edit: gettext('编辑'),
                    pause: gettext('暂停'),
                    collect: gettext('收藏'),
                    cancelCollection: gettext('取消收藏'),
                    addCollectSuccess: gettext('添加收藏成功！'),
                    cancelCollectSuccess: gettext('取消收藏成功！'),
                    totalRunCount: gettext('运行次数'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    periodicNamePlaceholder: gettext('请输入任务名称'),
                    creatorPlaceholder: gettext('请输入创建人'),
                    enabled: gettext('状态'),
                    periodicName: gettext('名称'),
                    editTitle: gettext('请暂停任务后再执行编辑操作'),
                    periodicTemplate: gettext('流程模板'),
                    executeHistory: gettext('执行历史'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    bootRecord: gettext('启动记录')
                },
                businessInfoLoading: true,
                isNewTaskDialogShow: false,
                listLoading: true,
                deleting: false,
                totalPage: 1,
                isDeleteDialogShow: false,
                isModifyDialogShow: false,
                isBootRecordDialogShow: false,
                selectedPeriodicId: undefined,
                periodicList: [],
                collectionList: [],
                selectedCron: undefined,
                constants: {},
                modifyDialogLoading: false,
                selectedTemplateName: undefined,
                periodEntrance: '',
                taskCategory: [],
                searchForm: searchForm,
                requestData: {
                    creator: '',
                    enabled: '',
                    flowName: this.$route.query.q || ''
                },
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
                },
                periodicOperations: [],
                periodicResource: {}
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
            this.getPeriodicList()
            this.getBizBaseInfo()
            this.getCollectList()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('periodic/', [
                'loadPeriodicList',
                'setPeriodicEnable',
                'getPeriodic',
                'deletePeriodic'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'addToCollectList',
                'deleteCollect',
                'loadCollectList'
            ]),
            async getPeriodicList () {
                this.listLoading = true
                try {
                    const { creator, enabled, flowName } = this.requestData
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        task__celery_task__enabled: enabled || undefined,
                        task__creator__contains: creator || undefined,
                        task__name__contains: flowName || undefined
                    }

                    if (!this.admin) {
                        data.project__id = this.project_id
                    }

                    const periodicListData = await this.loadPeriodicList(data)
                    const list = periodicListData.objects
                    this.periodicList = list
                    this.pagination.count = periodicListData.meta.total_count
                    this.periodicOperations = periodicListData.meta.auth_operations
                    this.periodicResource = periodicListData.meta.auth_resource
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.listLoading = false
                }
            },
            async getBizBaseInfo () {
                try {
                    const projectBasicInfo = await this.loadProjectBaseInfo()
                    this.taskCategory = projectBasicInfo.task_categories
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getCollectList () {
                try {
                    const res = await this.loadCollectList()
                    this.collectionList = res.objects
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.getPeriodicList()
            },
            /**
             * 单个周期任务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} periodic 模板数据对象
             * @params {Object} event 事件对象
             */
            onPeriodicPermissonCheck (required, periodic, event) {
                this.applyForPermission(required, periodic, this.periodicOperations, this.periodicResource)
                event.preventDefault()
            },
            onDeletePeriodic (periodic, event) {
                if (!this.hasPermission(['delete'], periodic.auth_actions, this.periodicOperations)) {
                    this.onPeriodicPermissonCheck(['delete'], periodic, event)
                    return
                }
                this.isDeleteDialogShow = true
                this.selectedDeleteTaskId = periodic.id
                this.selectedTemplateName = periodic.name
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getPeriodicList()
            },
            async onSetEnable (item, event) {
                if (!this.hasPermission(['edit'], item.auth_actions, this.periodicOperations)) {
                    this.onPeriodicPermissonCheck(['edit'], item, event)
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
                    errorHandler(e, this)
                }
            },
            onModifyCronPeriodic (item) {
                const { enabled, id: taskId, cron } = item
                if (!this.hasPermission(['edit'], item.auth_actions, this.periodicOperations)) {
                    this.onPeriodicPermissonCheck(['edit'], item, event)
                    return
                }
                if (enabled) {
                    return
                }
                const splitCron = this.splitPeriodicCron(cron)
                this.selectedCron = splitCron
                this.selectedPeriodicId = taskId
                this.getPeriodicConstant(taskId)
                this.isModifyDialogShow = true
            },
            onModifyPeriodicCancel () {
                this.isModifyDialogShow = false
            },
            onModifyPeriodicConfirm () {
                this.isModifyDialogShow = false
                this.getPeriodicList()
            },
            async getPeriodicConstant (taskId) {
                this.modifyDialogLoading = true
                const data = {
                    'taskId': taskId
                }
                const periodic = await this.getPeriodic(data)
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
                        'message': gettext('删除周期任务成功'),
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
                    errorHandler(e, this)
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
                this.isNewTaskDialogShow = true
            },
            onCreateTaskCancel () {
                this.isNewTaskDialogShow = false
            },
            onRecordView (task) {
                this.selectedPeriodicId = task.id
                this.isBootRecordDialogShow = true
            },
            templateNameUrl (templateId, templateSource) {
                const url = {
                    name: 'templatePanel',
                    params: { type: 'edit' },
                    query: { template_id: templateId, common: templateSource === 'common' || undefined }
                }
                return url
            },
            onSearchFormSubmit (data) {
                this.requestData = data
                this.getPeriodicList()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getPeriodicList()
            },
            // 添加/取消收藏模板
            async onCollectTask (template, event) {
                if (!this.hasPermission(['view'], template.auth_actions, this.periodicOperations)) {
                    this.onTemplatePermissonCheck(['view'], template, event)
                    return
                }
                try {
                    if (!this.isCollected(template.id)) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                project_id: template.project.id,
                                template_id: template.template_id,
                                name: template.name,
                                id: template.id
                            },
                            category: 'periodic_task'
                        }])
                        if (res.objects.length) {
                            this.$bkMessage({ message: this.i18n.addCollectSuccess, theme: 'success' })
                        }
                    } else { // cancel
                        const delId = this.collectionList.find(m => m.extra_info.id === template.id && m.category === 'periodic_task').id
                        await this.deleteCollect(delId)
                        this.$bkMessage({ message: this.i18n.cancelCollectSuccess, theme: 'success' })
                    }
                    this.getCollectList()
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            // 判断是否已在收藏列表
            isCollected (id) {
                return !!this.collectionList.find(m => m.extra_info.id === id && m.category === 'periodic_task')
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.list-wrapper {
    min-height: calc(100vh - 300px);
    .advanced-search {
        margin: 0px;
    }
    .operation-area{
        margin: 20px 0px;
        .task-create-btn {
            min-width: 120px;
        }
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
    }
    .icon-check-circle-shape {
        color: $greenDefault;
    }
    .common-icon-dark-circle-pause {
        color: #ff9C01;
        border-radius: 20px;
        font-size: 12px;
    }
    .drop-icon-ellipsis {
        font-size: 18px;
        vertical-align: -3px;
        cursor: pointer;
        &:hover {
            color: #3c96ff;
        }
    }
    .empty-data {
        padding: 120px 0;
    }
}
</style>
