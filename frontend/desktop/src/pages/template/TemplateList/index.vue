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
    <div class="template-container">
        <div class="list-wrapper">
            <list-page-tips-title
                :title="$t('项目流程')"
                :num="expiredSubflowTplList.length"
                @viewClick="handleSubflowFilter">
            </list-page-tips-title>
            <div class="operation-area clearfix">
                <advance-search-form
                    ref="advanceSearch"
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
                            {{$t('新建')}}
                        </bk-button>
                        <bk-button
                            theme="default"
                            class="template-btn"
                            @click="onExportTemplate">
                            {{$t('导出')}}
                        </bk-button>
                        <bk-button
                            theme="default"
                            class="template-btn"
                            @click="onImportTemplate">
                            {{ $t('导入') }}
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
                    <bk-table-column label="ID" prop="id" width="100"></bk-table-column>
                    <bk-table-column :label="$t('流程名称')">
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
                    <bk-table-column :label="$t('分类')" prop="category_name" width="180"></bk-table-column>
                    <bk-table-column :label="$t('更新时间')" prop="edit_time" width="200"></bk-table-column>
                    <bk-table-column
                        width="120"
                        :label="$t('子流程更新')">
                        <template slot-scope="props">
                            <div :class="['subflow-update', { 'subflow-has-update': props.row.subprocess_has_update }]">
                                {{getSubflowContent(props.row)}}
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('创建人')" prop="creator_name" width="140"></bk-table-column>
                    <bk-table-column :label="$t('操作')" width="240" class="operation-cell">
                        <template slot-scope="props">
                            <div class="template-operation">
                                <template>
                                    <a
                                        v-if="!hasPermission(['create_task'], props.row.auth_actions, tplOperations)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['create_task'], props.row, $event)">
                                        {{$t('新建任务')}}
                                    </a>
                                    <router-link
                                        v-else
                                        class="template-operate-btn"
                                        :to="getJumpUrl('newTask', props.row.id)">
                                        {{$t('新建任务')}}
                                    </router-link>
                                    <a
                                        v-if="!hasPermission(['clone'], props.row.auth_actions, tplOperations)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['clone'], props.row, $event)">
                                        {{$t('克隆')}}
                                    </a>
                                    <router-link
                                        v-else
                                        class="template-operate-btn"
                                        :to="getJumpUrl('clone', props.row.id)">
                                        {{$t('克隆')}}
                                    </router-link>
                                    <router-link
                                        class="template-operate-btn"
                                        :to="getExecuteHistoryUrl(props.row.id)">
                                        {{ $t('执行历史')}}
                                    </router-link>
                                    <bk-popover
                                        theme="light"
                                        placement="bottom-start"
                                        ext-cls="common-dropdown-btn-popver"
                                        :z-index="2000"
                                        :distance="0"
                                        :arrow="false"
                                        :tippy-options="{ boundary: 'window', duration: [0, 0] }">
                                        <i class="bk-icon icon-more drop-icon-ellipsis"></i>
                                        <ul slot="content">
                                            <li class="opt-btn">
                                                <a
                                                    v-cursor="{ active: !hasPermission(['view'], props.row.auth_actions, tplOperations) }"
                                                    href="javascript:void(0);"
                                                    :class="{
                                                        'disable': collectingId === props.row.id || collectListLoading,
                                                        'text-permission-disable': !hasPermission(['view'], props.row.auth_actions, tplOperations)
                                                    }"
                                                    @click="onCollectTemplate(props.row, $event)">
                                                    {{ isCollected(props.row.id) ? $t('取消收藏') : $t('收藏') }}
                                                </a>
                                            </li>
                                            <li class="opt-btn">
                                                <a
                                                    v-if="!hasPermission(['edit'], props.row.auth_actions, tplOperations)"
                                                    v-cursor
                                                    class="text-permission-disable"
                                                    @click="onTemplatePermissonCheck(['edit'], props.row, $event)">
                                                    {{$t('编辑')}}
                                                </a>
                                                <router-link
                                                    v-else
                                                    tag="a"
                                                    :to="getJumpUrl('edit', props.row.id)">
                                                    {{$t('编辑')}}
                                                </router-link>
                                            </li>
                                            <li class="opt-btn">
                                                <a
                                                    v-cursor="{ active: !hasPermission(['delete'], props.row.auth_actions, tplOperations) }"
                                                    href="javascript:void(0);"
                                                    :class="{
                                                        'text-permission-disable': !hasPermission(['delete'], props.row.auth_actions, tplOperations)
                                                    }"
                                                    @click="onDeleteTemplate(props.row, $event)">
                                                    {{ $t('删除') }}
                                                </a>
                                            </li>
                                        </ul>
                                    </bk-popover>
                                </template>
                            </div>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
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
            width="400"
            :mask-close="false"
            :header-position="'left'"
            :ext-cls="'common-dialog'"
            :title="$t('删除')"
            :value="isDeleteDialogShow"
            :auto-close="false"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div class="dialog-content" v-bkloading="{ isLoading: pending.delete, opacity: 1 }">
                {{$t('确认删除') + '"' + deleteTemplateName + '"' + '?' }}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import tools from '@/utils/tools.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import ImportTemplateDialog from './ImportTemplateDialog.vue'
    import ExportTemplateDialog from './ExportTemplateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    import ListPageTipsTitle from '../ListPageTipsTitle.vue'

    const searchForm = [
        {
            type: 'select',
            label: i18n.t('分类'),
            key: 'category',
            loading: false,
            placeholder: i18n.t('请选择分类'),
            list: []
        },
        {
            type: 'dateRange',
            key: 'queryTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('更新时间'),
            value: []
        },
        {
            type: 'select',
            label: i18n.t('子流程更新'),
            key: 'subprocessUpdateVal',
            placeholder: i18n.t('请选择'),
            list: [
                { 'value': 1, name: i18n.t('是') },
                { 'value': -1, name: i18n.t('否') },
                { 'value': 0, name: i18n.t('无子流程') }
            ],
            value: ''
        },
        {
            type: 'input',
            key: 'creator',
            label: i18n.t('创建人'),
            placeholder: i18n.t('请输入创建人'),
            value: ''
        }
    ]
    export default {
        name: 'TemplateList',
        components: {
            CopyrightFooter,
            ImportTemplateDialog,
            ExportTemplateDialog,
            ListPageTipsTitle,
            AdvanceSearchForm,
            NoData
        },
        mixins: [permission],
        props: ['project_id'],
        data () {
            return {
                listLoading: true,
                projectInfoLoading: true, // 模板分类信息 loading
                searchStr: '',
                searchForm: tools.deepClone(searchForm),
                expiredSubflowTplList: [],
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
                totalPage: 1,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
                },
                collectingId: '', // 正在被收藏/取消收藏的模板id
                collectListLoading: false,
                collectionList: [],
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
            })
        },
        created () {
            this.getTemplateList()
            this.getProjectBaseInfo()
            this.getExpiredSubflowData()
            this.getCollectList()
            this.onSearchInput = tools.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('template/', [
                'addToCollectList',
                'deleteCollect',
                'loadCollectList',
                'loadProjectBaseInfo'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList',
                'deleteTemplate',
                'saveTemplatePersons',
                'templateImport',
                'templateExport',
                'getExpiredSubProcess'
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

                    /**
                     * 无子流程 has_subprocess=false
                     * 有子流程，需要更新 has_subprocess=true&subprocess_has_update=true
                     * 有子流程，不需要更新 has_subprocess=true&subprocess_has_update=false
                     */
                    const has_subprocess = (subprocessUpdateVal === 1 || subprocessUpdateVal === -1)
                    const subprocess_has_update = subprocessUpdateVal === 1 ? true : (subprocessUpdateVal === -1 ? false : undefined)
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        pipeline_template__name__contains: flowName || undefined,
                        pipeline_template__creator__contains: creator || undefined,
                        category: category || undefined,
                        subprocess_has_update,
                        has_subprocess
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
                    this.searchForm[0].list = data.task_categories
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.projectInfoLoading = false
                    this.searchForm[0].loading = false
                }
            },
            async getExpiredSubflowData () {
                try {
                    const resp = await this.getExpiredSubProcess({ project__id: this.project_id })
                    if (resp.result) {
                        this.expiredSubflowTplList = resp.data
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            async getCollectList () {
                try {
                    this.collectListLoading = true
                    const res = await this.loadCollectList()
                    this.collectionList = res.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.collectListLoading = false
                }
            },
            checkCreatePermission () {
                if (!this.hasPermission(this.createTplRequired, this.authActions, this.authOperations)) {
                    const resourceData = {
                        name: i18n.t('项目'),
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
            // 获得表格中“子流程更新”列展示内容
            getSubflowContent (item) {
                if (!item.has_subprocess) {
                    return '--'
                }
                return item.subprocess_has_update ? i18n.t('是') : i18n.t('否')
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getTemplateList()
            },
            // 标题提示信息，查看子流程更新
            handleSubflowFilter () {
                const searchComp = this.$refs.advanceSearch
                searchComp.onAdvanceOpen(true)
                searchComp.onChangeFormItem(1, searchForm[2].key)
                searchComp.submit()
            },
            // 添加/取消收藏模板
            async onCollectTemplate (template, event) {
                if (!this.hasPermission(['view'], template.auth_actions, this.tplOperations)) {
                    this.onTemplatePermissonCheck(['view'], template, event)
                    return
                }

                if (typeof this.collectingId === 'number') {
                    return
                }

                try {
                    this.collectingId = template.id
                    if (!this.isCollected(template.id)) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                project_id: template.project.id,
                                template_id: template.template_id,
                                template_source: template.template_source,
                                name: template.name,
                                id: template.id
                            },
                            category: 'flow'
                        }])
                        if (res.objects.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                    } else { // cancel
                        const delId = this.collectionList.find(m => m.extra_info.id === template.id && m.category === 'flow').id
                        await this.deleteCollect(delId)
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                    }
                    this.getCollectList()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.collectingId = ''
                }
            },
            // 判断是否已在收藏列表
            isCollected (id) {
                return !!this.collectionList.find(m => m.extra_info.id === id && m.category === 'flow')
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
}
.template-table-content {
    background: #ffffff;
    a.template-name {
        color: $blueDefault;
    }
    .template-operation > .text-permission-disable {
        padding: 5px;
    }
    .template-operate-btn {
        padding: 5px;
        color: #3a84ff;
    }
    .drop-icon-ellipsis {
        display: inline-block;
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
    .subflow-has-update {
        color: $redDefault;
    }
}
</style>
