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
    <div class="template-container">
        <div class="list-wrapper">
            <base-title :title="i18n.projectFlow"></base-title>
            <div class="operation-area clearfix">
                <advance-search-form
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            v-cursor="{ active: !hasPermission(createTplRequired, authActions, authOperations) }"
                            theme="primary"
                            :class="['create-template', {
                                'btn-permission-disable': !hasPermission(createTplRequired, authActions, authOperations)
                            }]"
                            @click="checkCreatePermission">
                            {{i18n.new}}
                        </bk-button>
                        <bk-button
                            theme="default"
                            class="template-btn"
                            @click="onExportTemplate">
                            {{i18n.export}}
                        </bk-button>
                        <bk-button
                            theme="default"
                            class="template-btn"
                            @click="onImportTemplate">
                            {{ i18n.import }}
                        </bk-button>
                    </template>
                </advance-search-form>
            </div>
            <div class="template-table-content">
                <bk-table
                    class="template-table"
                    :data="templateList"
                    :pagination="pagination"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }"
                    @page-change="onPageChange"
                    @page-limit-change="handlePageLimitChange">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="i18n.name">
                        <template slot-scope="props">
                            <template>
                                <a
                                    v-if="!hasPermission(['view'], props.row.auth_actions, tplOperations)"
                                    v-cursor
                                    class="text-permission-disable"
                                    @click="onTemplatePermissonCheck(['view'], props.row, $event)">
                                    {{props.row.name}}
                                </a>
                                <router-link
                                    v-else
                                    class="template-name"
                                    :title="props.row.name"
                                    :to="getJumpUrl('edit', props.row.id)">
                                    {{props.row.name}}
                                </router-link>
                            </template>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.type" prop="category_name"></bk-table-column>
                    <bk-table-column :label="i18n.updateTime" prop="edit_time"></bk-table-column>
                    <bk-table-column
                        width="120"
                        :label="i18n.subflowUpdate">
                        <template slot-scope="props">
                            <div :class="['subflow-update', { 'subflow-has-update': props.row.subprocess_has_update }]">
                                {{getSubflowContent(props.row)}}
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator_name" width="120"></bk-table-column>
                    <bk-table-column :label="i18n.operation" width="180" class="operation-cell">
                        <template slot-scope="props">
                            <div class="template-operation">
                                <template>
                                    <!-- 项目流程按钮 -->
                                    <a
                                        v-if="!hasPermission(['create_task'], props.row.auth_actions, tplOperations)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['create_task'], props.row, $event)">
                                        {{i18n.newTemplate}}
                                    </a>
                                    <router-link
                                        v-else
                                        class="template-operate-btn"
                                        :to="getJumpUrl('newTask', props.row.id)">
                                        {{i18n.newTemplate}}
                                    </router-link>
                                    <a
                                        v-if="!hasPermission(['edit'], props.row.auth_actions, tplOperations)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['edit'], props.row, $event)">
                                        {{i18n.edit}}
                                    </a>
                                    <router-link
                                        v-else
                                        class="template-operate-btn"
                                        :to="getJumpUrl('edit', props.row.id)">
                                        {{i18n.edit}}
                                    </router-link>
                                    <bk-dropdown-menu>
                                        <i slot="dropdown-trigger" class="bk-icon icon-more drop-icon-ellipsis"></i>
                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                            <li>
                                                <a
                                                    v-if="!hasPermission(['clone'], props.row.auth_actions, tplOperations)"
                                                    v-cursor
                                                    class="text-permission-disable"
                                                    @click="onTemplatePermissonCheck(['clone'], props.row, $event)">
                                                    {{i18n.clone}}
                                                </a>
                                                <router-link
                                                    v-else
                                                    :to="getJumpUrl('clone', props.row.id)">
                                                    {{i18n.clone}}
                                                </router-link>
                                            </li>
                                            <li>
                                                <router-link :to="getExecuteHistoryUrl(props.row.id)">{{ i18n.executeHistory }}</router-link>
                                            </li>
                                            <li>
                                                <a
                                                    v-cursor="{ active: !hasPermission(['delete'], props.row.auth_actions, tplOperations) }"
                                                    href="javascript:void(0);"
                                                    :class="{
                                                        'text-permission-disable': !hasPermission(['delete'], props.row.auth_actions, tplOperations)
                                                    }"
                                                    @click="onDeleteTemplate(props.row, $event)">
                                                    {{ i18n.delete }}
                                                </a>
                                            </li>
                                        </ul>
                                    </bk-dropdown-menu>
                                </template>
                            </div>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="i18n.empty" /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <ImportTemplateDialog
            :is-import-dialog-show="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportTemplateDialog>
        <ExportTemplateDialog
            :is-export-dialog-show="isExportDialogShow"
            :project-info-loading="projectInfoLoading"
            :pending="pending.export"
            @onExportConfirm="onExportConfirm"
            @onExportCancel="onExportCancel">
        </ExportTemplateDialog>
        <bk-dialog
            :mask-close="false"
            :header-position="'left'"
            :ext-cls="'common-dialog'"
            :title="i18n.delete"
            width="400"
            :value="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div class="dialog-content" v-bkloading="{ isLoading: pending.delete, opacity: 1 }">
                {{i18n.deleleTip + '"' + deleteTemplateName + '"' + '?' }}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import ImportTemplateDialog from './ImportTemplateDialog.vue'
    import ExportTemplateDialog from './ExportTemplateDialog.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    const searchForm = [
        {
            type: 'select',
            label: gettext('分类'),
            key: 'category',
            loading: false,
            placeholder: gettext('请选择分类'),
            list: []
        },
        {
            type: 'dateRange',
            key: 'queryTime',
            placeholder: gettext('选择日期时间范围'),
            label: gettext('更新时间'),
            value: []
        },
        {
            type: 'select',
            label: gettext('子流程更新'),
            key: 'subprocessUpdateVal',
            placeholder: gettext('请选择'),
            list: [
                { 'value': 1, name: gettext('是') },
                { 'value': -1, name: gettext('否') },
                { 'value': 0, name: gettext('无子流程') }
            ]
        },
        {
            type: 'input',
            key: 'creator',
            label: gettext('创建人'),
            placeholder: gettext('请输入创建人'),
            value: ''
        }
    ]
    export default {
        name: 'TemplateList',
        components: {
            CopyrightFooter,
            ImportTemplateDialog,
            ExportTemplateDialog,
            AdvanceSearchForm,
            BaseTitle,
            NoData
        },
        mixins: [permission],
        props: ['project_id'],
        data () {
            return {
                i18n: {
                    placeholder: gettext('请输入ID或流程名称'),
                    projectFlow: gettext('项目流程'),
                    new: gettext('新建'),
                    name: gettext('流程名称'),
                    type: gettext('分类'),
                    updateTime: gettext('更新时间'),
                    subflowUpdate: gettext('子流程更新'),
                    creator: gettext('创建人'),
                    operation: gettext('操作'),
                    newTemplate: gettext('新建任务'),
                    edit: gettext('编辑'),
                    clone: gettext('克隆'),
                    delete: gettext('删除'),
                    executeHistory: gettext('执行历史'),
                    deleleTip: gettext('确认删除'),
                    import_v1_template: gettext('导入 V1 模板'),
                    export: gettext('导出'),
                    import: gettext('导入'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    yes: gettext('是'),
                    no: gettext('否'),
                    empty: gettext('无数据'),
                    templateNamePlaceholder: gettext('请输入流程名称'),
                    subprocessUpdatePlaceholder: gettext('请选择子流程更新'),
                    templateType: gettext('来源'),
                    templateTypePlaceholder: gettext('请选择来源'),
                    select: gettext('请选择'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    templateName: gettext('名称'),
                    advanceSearch: gettext('高级搜索'),
                    searchName: gettext('搜索流程名称')
                },
                listLoading: true,
                projectInfoLoading: true, // 模板分类信息 loading
                searchStr: '',
                totalPage: 1,
                isDeleteDialogShow: false,
                isImportDialogShow: false,
                isExportDialogShow: false,
                isAuthorityDialogShow: false,
                theDeleteTemplateId: undefined,
                theAuthorityManageId: undefined,
                active: true,
                pending: {
                    export: false, // 导出
                    delete: false // 删除
                },
                templateCategoryList: [],
                editEndTime: undefined,
                isSubprocessUpdated: undefined,
                isHasSubprocess: undefined,
                deleteTemplateName: '',
                requestData: {
                    category: '',
                    queryTime: [],
                    subprocessUpdateVal: '',
                    creator: '',
                    flowName: ''
                },
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
                },
                createTplRequired: ['create_template'],
                tplOperations: [], // 模板权限字典
                tplResource: {}, // 模板资源信息
                createCommonTplAction: [] // 创建公共流程权限
            }
        },
        computed: {
            ...mapState({
                'site_url': state => state.site_url,
                'templateList': state => state.templateList.templateListData,
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'v1_import_flag': state => state.v1_import_flag
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'authActions': state => state.authActions,
                'authOperations': state => state.authOperations,
                'authResource': state => state.authResource,
                'projectName': state => state.projectName
            }),
            searchForm () {
                const value = searchForm
                value[0].list = this.templateCategoryList
                value[0].loading = this.categoryLoading
                return searchForm
            }
        },
        created () {
            this.getTemplateList()
            this.getProjectBaseInfo()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList',
                'deleteTemplate',
                'saveTemplatePersons',
                'templateImport',
                'templateExport'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            ...mapMutations('templateList/', [
                'setTemplateListData'
            ]),
            async getTemplateList () {
                this.listLoading = true
                try {
                    const { subprocessUpdateVal, creator, category, queryTime, flowName } = this.requestData
                    const has_subprocess = (subprocessUpdateVal === '' || subprocessUpdateVal === 0) ? undefined : (subprocessUpdateVal > 0)
                    const subprocess_has_update = subprocessUpdateVal === '' ? undefined : (subprocessUpdateVal !== 0)
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        pipeline_template__name__contains: flowName || undefined,
                        pipeline_template__creator__contains: creator || undefined,
                        category: category || undefined,
                        subprocess_has_update,
                        has_subprocess
                    }
                    if (this.flowName) {
                        data['pipeline_template__name__contains'] = this.flowName
                    }

                    if (this.creator) {
                        data['pipeline_template__creator__contains'] = this.creator
                    }

                    if (this.category) {
                        data['category'] = this.category
                    }

                    if (this.isHasSubprocess !== undefined) {
                        data['subprocess_has_update'] = this.isSubprocessUpdated
                        data['has_subprocess'] = this.isHasSubprocess
                    }

                    if (queryTime[0] && queryTime[1]) {
                        data['pipeline_template__edit_time__gte'] = moment.tz(queryTime[0], this.timeZone).format('YYYY-MM-DD')
                        data['pipeline_template__edit_time__lte'] = moment.tz(queryTime[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                    }

                    const templateListData = await this.loadTemplateList(data)
                    const list = templateListData.objects
                    this.setTemplateListData({ list, isCommon: false })
                    this.pagination.count = templateListData.meta.total_count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    this.tplOperations = templateListData.meta.auth_operations
                    this.tplResource = templateListData.meta.auth_resource
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
            async getProjectBaseInfo () {
                this.projectInfoLoading = true
                this.categoryLoading = true
                try {
                    const data = await this.loadProjectBaseInfo()
                    this.setProjectBaseInfo(data)
                    this.templateCategoryList = data.task_categories
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.projectInfoLoading = false
                    this.categoryLoading = false
                }
            },
            checkCreatePermission () {
                if (!this.hasPermission(this.createTplRequired, this.authActions, this.authOperations)) {
                    const resourceData = {
                        name: gettext('项目'),
                        id: this.project_id,
                        auth_actions: this.authActions
                    }
                    this.applyForPermission(this.createTplRequired, resourceData, this.authOperations, this.authResource)
                } else {
                    this.$router.push({
                        name: 'templatePanel',
                        params: { type: 'new', project_id: this.project_id }
                    })
                }
            },
            onSearchFormSubmit (data) {
                this.requestData = data
                this.getTemplateList()
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.getTemplateList()
            },
            onImportTemplate () {
                this.isImportDialogShow = true
            },
            onImportConfirm () {
                this.isImportDialogShow = false
                this.getTemplateList()
            },
            onImportCancel () {
                this.isImportDialogShow = false
            },
            onExportTemplate () {
                this.isExportDialogShow = true
            },
            async onExportConfirm (list) {
                if (this.pending.export) return
                this.pending.export = true
                try {
                    const data = {
                        list: list
                    }
                    const resp = await this.templateExport(data)
                    if (resp.result) {
                        this.isExportDialogShow = false
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending.export = false
                }
            },
            onExportCancel () {
                this.isExportDialogShow = false
            },
            onDeleteTemplate (template, event) {
                if (!this.hasPermission(['delete'], template.auth_actions, this.tplOperations)) {
                    this.onTemplatePermissonCheck(['delete'], template, event)
                    return
                }
                this.theDeleteTemplateId = template.id
                this.deleteTemplateName = template.name
                this.isDeleteDialogShow = true
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getTemplateList()
            },
            /**
             * 单个模板操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 模板数据对象
             * @params {Object} event 事件对象
             */
            onTemplatePermissonCheck (required, template, event) {
                this.applyForPermission(required, template, this.tplOperations, this.tplResource)
                event.preventDefault()
            },
            async onDeleteConfirm () {
                if (this.pending.delete) return
                this.pending.delete = true
                try {
                    const data = {
                        templateId: this.theDeleteTemplateId
                    }
                    await this.deleteTemplate(data)
                    this.theDeleteTemplateId = undefined
                    this.isDeleteDialogShow = false
                    // 最后一页最后一条删除后，往前翻一页
                    if (
                        this.pagination.current > 1
                        && this.totalPage === this.pagination.current
                        && this.pagination.count - (this.totalPage - 1) * this.pagination.limit === 1
                    ) {
                        this.pagination.current -= 1
                    }
                    this.getTemplateList()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending.delete = false
                }
            },
            onDeleteCancel () {
                this.theDeleteTemplateId = undefined
                this.isDeleteDialogShow = false
            },
            async onAuthorityConfirm (data) {
                if (this.pending.authority) return
                this.pending.authority = true
                try {
                    await this.saveTemplatePersons(data)
                    this.isAuthorityDialogShow = false
                    this.theAuthorityManageId = undefined
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending.authority = false
                }
            },
            onAuthorityCancel () {
                this.isAuthorityDialogShow = false
                this.theAuthorityManageId = undefined
            },
            /**
             * 获取模版操作的跳转链接
             * @param {string} name -类型
             * @param {Number} template_id -模版id(可选)
             */
            getJumpUrl (name, template_id) {
                const urlMap = {
                    'edit': { name: 'templatePanel', params: { type: 'edit' } },
                    'newTemplate': { name: 'templatePanel', params: { type: 'new' } },
                    'newTask': { name: 'taskStep', params: { project_id: this.project_id, step: 'selectnode' } },
                    'clone': { name: 'templatePanel', params: { type: 'clone' } }
                }
                const url = urlMap[name]
                url.query = {
                    template_id
                }
                return url
            },
            getExecuteHistoryUrl (id) {
                return {
                    name: 'taskList',
                    params: { project_id: this.project_id },
                    query: { template_id: id }
                }
            },
            // 获得子流程展示内容
            getSubflowContent (item) {
                if (!item.has_subprocess) {
                    return '--'
                }
                return item.subprocess_has_update ? this.i18n.yes : this.i18n.no
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getTemplateList()
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.dialog-content {
    padding: 30px;
    word-break: break-all;
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
}
.operation-area {
    margin: 20px 0;
    .create-template {
        min-width: 120px;
        font-size: 14px;
    }
    .template-btn {
        margin-left: 5px;
    }
    .template-search {
        height: 156px;
        background: #fff;
    }
    .template-advanced-search {
        float: right;
        .base-search {
            margin: 0px;
        }
    }
}
.template-table-content {
    background: #ffffff;
    a.template-name {
        color: $blueDefault;
    }
    /deep/ .bk-table {
        overflow: visible;
        .bk-table-body-wrapper,.is-scrolling-none,
        td.is-last .cell {
            overflow: visible;
        }
    }
    .template-operation > .text-permission-disable {
        padding: 5px;
    }
    .template-operate-btn {
        padding: 5px;
        color: #3c96ff;
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
    .subflow-has-update {
        color: $redDefault;
    }
}
.bk-dropdown-menu .bk-dropdown-list > li > a {
    font-size: 12px;
}
</style>
