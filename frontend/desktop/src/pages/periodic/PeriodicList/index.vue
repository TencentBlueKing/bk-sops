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
    <div class="periodic-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.periodicTask"></BaseTitle>
            <div class="operation-area">
                <bk-button
                    ref="childComponent"
                    theme="primary"
                    class="task-create-btn"
                    size="normal"
                    @click="onCreatePeriodTask">
                    {{i18n.createPeriodTask}}
                </bk-button>
                <AdvanceSearch
                    v-model="periodicName"
                    class="base-search"
                    :input-placeholader="i18n.periodicNamePlaceholder"
                    @onShow="onAdvanceShow"
                    @input="onSearchInput">
                </AdvanceSearch>
            </div>
            <div v-show="isAdvancedSerachShow" class="periodic-search">
                <fieldset class="periodic-fieldset">
                    <div class="periodic-query-content">
                        <div class="query-content">
                            <span class="query-span">{{i18n.creator}}</span>
                            <bk-input
                                v-model="creator"
                                class="bk-input-inline"
                                :clearable="true"
                                :placeholder="i18n.creatorPlaceholder">
                            </bk-input>
                        </div>
                        <div class="query-content">
                            <span class="query-span">{{i18n.enabled}}</span>
                            <bk-select
                                class="bk-select-inline"
                                v-model="enabledSync"
                                :popover-width="260"
                                :placeholder="i18n.enabledPlaceholder"
                                :clearable="true"
                                @clear="onClearSelectedEnabled"
                                @selected="onSelectEnabled">
                                <bk-option
                                    v-for="(option, index) in enabledList"
                                    :key="index"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="query-button">
                            <bk-button class="query-primary" theme="primary" @click="searchInputhandler">{{i18n.query}}</bk-button>
                            <bk-button class="query-cancel" @click="onResetForm">{{i18n.reset}}</bk-button>
                        </div>
                    </div>
                </fieldset>
            </div>
            <div class="periodic-table-content">
                <bk-table
                    :data="periodicList"
                    :pagination="pagination"
                    @page-change="onPageChange"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="i18n.periodicName" prop="name">
                        <template slot-scope="props">
                            <span :title="props.row.name">{{props.row.name}}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.periodicTemplate">
                        <template slot-scope="props">
                            <router-link
                                class="periodic-name"
                                :title="props.row.task_template_name"
                                :to="`/template/edit/${cc_id}/?template_id=${props.row.template_id}`">
                                {{props.row.task_template_name}}
                            </router-link>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.periodicRule">
                        <template slot-scope="props">
                            <div :title="splitPeriodicCron(props.row.cron)">{{ splitPeriodicCron(props.row.cron) }}</div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.lastRunAt">
                        <template slot-scope="props">
                            <div>{{ props.row.last_run_at || '--' }}</div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator" width="120"></bk-table-column>
                    <bk-table-column :label="i18n.totalRunCount" prop="total_run_count" width="130"></bk-table-column>
                    <bk-table-column :label="i18n.enabled" width="120">
                        <template slot-scope="props" class="periodic-status">
                            <span :class="props.row.enabled ? 'bk-icon icon-check-circle-shape' : 'common-icon-dark-circle-pause'"></span>
                            {{props.row.enabled ? i18n.start : i18n.pause}}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.operation" width="140">
                        <template slot-scope="props">
                            <div class="periodic-operation">
                                <a
                                    href="javascript:void(0);"
                                    :class="['periodic-pause-btn', { 'periodic-start-btn': !props.row.enabled }]"
                                    @click="onSetEnable(props.row)">
                                    {{!props.row.enabled ? i18n.start : i18n.pause}}
                                </a>
                                <a
                                    href="javascript:void(0);"
                                    :class="['periodic-bk-btn', { 'periodic-bk-disable': props.row.enabled }]"
                                    :title="props.row.enabled ? i18n.editTitle : ''"
                                    @click="onModifyCronPeriodic(props.row)">
                                    {{ i18n.edit }}
                                </a>
                                <bk-dropdown-menu>
                                    <i slot="dropdown-trigger" class="bk-icon icon-more drop-icon-ellipsis"></i>
                                    <ul
                                        slot="dropdown-content"
                                        class="bk-dropdown-list">
                                        <li>
                                            <a href="javascript:void(0);" @click="onDeletePeriodic(props.row.id, props.row.name)">{{ i18n.delete }}</a>
                                        </li>
                                        <li>
                                            <router-link :to="`/taskflow/home/${cc_id}/?template_id=${props.row.template_id}&create_method=periodic`">
                                                {{ i18n.executeHistory }}
                                            </router-link>
                                        </li>
                                    </ul>
                                </bk-dropdown-menu>
                            </div>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="i18n.empty" /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <TaskCreateDialog
            :cc_id="cc_id"
            :is-new-task-dialog-show="isNewTaskDialogShow"
            :business-info-loading="businessInfoLoading"
            :create-entrance="false"
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
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearch from '@/components/common/base/AdvanceSearch.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskCreateDialog from '../../task/TaskList/TaskCreateDialog.vue'
    import ModifyPeriodicDialog from './ModifyPeriodicDialog.vue'
    import DeletePeriodicDialog from './DeletePeriodicDialog.vue'
    export default {
        name: 'PeriodicList',
        components: {
            CopyrightFooter,
            BaseTitle,
            AdvanceSearch,
            NoData,
            TaskCreateDialog,
            ModifyPeriodicDialog,
            DeletePeriodicDialog
        },
        props: ['cc_id', 'common'],
        data () {
            return {
                i18n: {
                    createPeriodTask: gettext('新建'),
                    dialogTitle: gettext('新建周期任务'),
                    lastRunAt: gettext('上次运行时间'),
                    periodicRule: gettext('周期规则'),
                    periodicTask: gettext('周期任务'),
                    advanceSearch: gettext('高级搜索'),
                    creator: gettext('创建人'),
                    operation: gettext('操作'),
                    start: gettext('启动'),
                    delete: gettext('删除'),
                    edit: gettext('编辑'),
                    pause: gettext('暂停'),
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
                    enabledPlaceholder: gettext('请选择状态'),
                    periodicTemplate: gettext('流程模板'),
                    executeHistory: gettext('执行历史'),
                    query: gettext('搜索'),
                    reset: gettext('清空')
                },
                businessInfoLoading: true,
                isNewTaskDialogShow: false,
                listLoading: true,
                deleting: false,
                totalPage: 1,
                isDeleteDialogShow: false,
                isAdvancedSerachShow: false,
                creator: undefined,
                enabled: undefined,
                enabledList: [
                    { 'id': 'true', 'name': gettext('启动') },
                    { 'id': 'false', 'name': gettext('暂停') }
                ],
                selectedPeriodicId: undefined,
                periodicList: [],
                isModifyDialogShow: false,
                selectedCron: undefined,
                constants: {},
                modifyDialogLoading: false,
                selectedTemplateName: undefined,
                periodicName: undefined,
                enabledSync: '',
                periodEntrance: '',
                taskCategory: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15],
                    'show-limit': false
                }
            }
        },
        created () {
            this.getPeriodicList()
            this.getBizBaseInfo()
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
                'loadBusinessBaseInfo'
            ]),
            async getPeriodicList () {
                this.listLoading = true
                try {
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        task__celery_task__enabled: this.enabled,
                        task__creator__contains: this.creator,
                        task__name__contains: this.periodicName || undefined
                    }
                    const periodicListData = await this.loadPeriodicList(data)
                    const list = periodicListData.objects
                    this.periodicList = list
                    this.pagination.count = periodicListData.meta.total_count
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
                    const bizBasicInfo = await this.loadBusinessBaseInfo()
                    this.taskCategory = bizBasicInfo.task_categories
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            searchInputhandler () {
                this.pagination.current = 1
                this.getPeriodicList()
            },
            onDeletePeriodic (id, name) {
                this.isDeleteDialogShow = true
                this.selectedDeleteTaskId = id
                this.selectedTemplateName = name
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getPeriodicList()
            },
            onSelectEnabled (enabled) {
                this.enabled = enabled
            },
            async onSetEnable (item) {
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
            onClearSelectedEnabled () {
                this.enabled = undefined
            },
            splitPeriodicCron (cron) {
                return cron.split('(')[0].trim()
            },
            onResetForm () {
                this.periodicName = undefined
                this.creator = undefined
                this.enabled = undefined
                this.enabledSync = ''
                this.searchInputhandler()
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onCreatePeriodTask () {
                this.isNewTaskDialogShow = true
            },
            onCreateTaskCancel () {
                this.isNewTaskDialogShow = false
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
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
.periodic-fieldset {
    width: 100%;
    margin-bottom: 15px;
    border: 1px solid $commonBorderColor;
    background: #ffffff;
    padding: 8px;
    .periodic-query-content {
        display: flex;
        flex-wrap: wrap;
        .query-content {
            min-width: 420px;
            padding: 10px;
            @media screen and (max-width: 1420px){
                min-width: 380px;
            }
            .query-span {
                float: left;
                min-width: 130px;
                margin-right: 12px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                text-align: right;
                @media screen and (max-width: 1420px){
                    min-width: 100px;
                }
            }
            .bk-select-inline {
                display: inline-block;
                width: 260px;
            }
            .bk-input-inline {
                display: inline-block;
                width: 260px;
            }
            // 浏览兼容样式
            input::-webkit-input-placeholder{
                color: $formBorderColor;
            }
            input:-moz-placeholder {
                color: $formBorderColor;
            }
            input::-moz-placeholder {
                color: $formBorderColor;
            }
            input:-ms-input-placeholder {
                color: $formBorderColor;
            }
            .bk-selector-search-item > input {
                min-width: 249px;
            }
            .search-input {
                width: 260px;
                height: 32px;
                padding: 0 32px 0 10px;
                font-size: 14px;
                color: $greyDefault;
                border: 1px solid $formBorderColor;
                line-height: 32px;
                outline: none;
                &:hover {
                    border-color: #c0c4cc;
                }
                &:focus {
                    border-color: $blueDefault;
                    & + i {
                        color: $blueDefault;
                    }
                }
            }
            .search-input.placeholder {
                color: $formBorderColor;
            }
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
        overflow: visible;
        .bk-table-body-wrapper,.is-scrolling-none,
        td.is-last .cell {
            overflow: visible;
        }
    }
    .icon-check-circle-shape {
        color: #30d878;
    }
    a.periodic-name,
    .periodic-operation a {
        color: $blueDefault;
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
        position: absolute;
        top: -13px;
        font-size: 18px;
        cursor: pointer;
        &:hover {
            color: #3c96ff;
        }
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
.btn-size-mini {
    height: 24px;
    line-height: 22px;
    padding: 0 11px;
    font-size: 12px;
}
.bk-dropdown-menu .bk-dropdown-list > li > a {
    font-size: 12px;
}
</style>
