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
                :title="$t('公共流程')"
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
                            v-cursor="{ active: !hasPermission(createTplRequired, createCommonTplAction, tplOperations) }"
                            theme="primary"
                            :class="['create-template', {
                                'btn-permission-disable': !hasPermission(createTplRequired, createCommonTplAction, tplOperations)
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
                    :data="commonTemplateData"
                    :pagination="pagination"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }"
                    @page-change="onPageChange"
                    @page-limit-change="handlePageLimitChange">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="$t('流程名称')" min-width="200">
                        <template slot-scope="props">
                            <a
                                v-if="!hasPermission(['view'], props.row.auth_actions, tplOperations)"
                                v-cursor
                                class="text-permission-disable"
                                @click="onTemplatePermissonCheck(['view'], props.row, $event)">
                                {{props.row.name}}
                            </a>
                            <a
                                v-else
                                class="template-name"
                                :title="props.row.name"
                                @click.prevent="getJumpUrl('edit', props.row.id)">
                                {{props.row.name}}
                            </a>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('分类')" prop="category_name" width="180"></bk-table-column>
                    <bk-table-column :label="$t('更新时间')" prop="edit_time" width="200"></bk-table-column>
                    <bk-table-column width="120" :label="$t('子流程更新')">
                        <template slot-scope="props">
                            <div :class="['subflow-update', { 'subflow-has-update': props.row.subprocess_has_update }]">
                                {{getSubflowContent(props.row)}}
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('创建人')" prop="creator_name" width="120"></bk-table-column>
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
                                    <a
                                        v-else
                                        class="template-operate-btn"
                                        @click.prevent="getJumpUrl('newTask', props.row.id)">
                                        {{$t('新建任务')}}
                                    </a>
                                    <a
                                        v-if="!hasPermission(['clone'], props.row.auth_actions, tplOperations)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['clone'], props.row, $event)">
                                        {{$t('克隆')}}
                                    </a>
                                    <a
                                        v-else
                                        class="template-operate-btn"
                                        @click.prevent="getJumpUrl('clone', props.row.id)">
                                        {{$t('克隆')}}
                                    </a>
                                    <router-link class="template-operate-btn" :to="getExecuteHistoryUrl(props.row.id)">{{ $t('执行历史') }}</router-link>
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
                                                <a
                                                    v-else
                                                    class="template-operate-btn"
                                                    @click.prevent="getJumpUrl('edit', props.row.id)">
                                                    {{$t('编辑')}}
                                                </a>
                                            </li>
                                            <li class="opt-btn">
                                                <a
                                                    v-cursor="{ active: !hasPermission(['delete'], props.row.auth_actions, tplOperations) }"
                                                    href="javascript:void(0);"
                                                    :class="{
                                                        'text-permission-disable': !hasPermission(['delete'], props.row.auth_actions, tplOperations)
                                                    }"
                                                    @click="onDeleteTemplate(props.row, $event)">
                                                    {{$t('删除')}}
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
            common="1"
            :is-import-dialog-show="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportTemplateDialog>
        <ExportTemplateDialog
            common="1"
            :is-export-dialog-show="isExportDialogShow"
            :project-info-loading="projectInfoLoading"
            :pending="pending.export"
            @onExportConfirm="onExportConfirm"
            @onExportCancel="onExportCancel">
        </ExportTemplateDialog>
        <ProjectSelectorModal
            ref="ProjectSelectorModal"
            @confirm="selectedProjectToNewTask">
        </ProjectSelectorModal>
        <bk-dialog
            :mask-close="false"
            :header-position="'left'"
            :ext-cls="'common-dialog'"
            :title="$t('删除')"
            width="400"
            :value="isDeleteDialogShow"
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
    import toolsUtils from '@/utils/tools.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import ImportTemplateDialog from '../TemplateList/ImportTemplateDialog.vue'
    import ExportTemplateDialog from '../TemplateList/ExportTemplateDialog.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import ProjectSelectorModal from '@/components/common/modal/ProjectSelectorModal.vue'
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
            ]
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
            ProjectSelectorModal,
            ListPageTipsTitle,
            AdvanceSearchForm,
            NoData
        },
        mixins: [permission],
        data () {
            return {
                listLoading: true,
                projectInfoLoading: true, // 模板分类信息 loading
                searchStr: '',
                expiredSubflowTplList: [],
                isDeleteDialogShow: false,
                isImportDialogShow: false,
                isExportDialogShow: false,
                isAuthorityDialogShow: false,
                isShowProjectSelector: false,
                theDeleteTemplateId: undefined,
                theAuthorityManageId: undefined,
                active: true,
                pending: {
                    export: false, // 导出
                    delete: false // 删除
                },
                templateCategoryList: [],
                collectListLoading: false,
                collectionList: [],
                category: undefined,
                editEndTime: undefined,
                templateType: this.common_template,
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
                createTplRequired: ['create'],
                collectingId: '', // 正在被收藏/取消收藏的模板id
                tplOperations: [], // 模板权限字典
                tplResource: {}, // 模板资源信息
                createCommonTplAction: [] // 创建公共流程权限
            }
        },
        computed: {
            ...mapState({
                'site_url': state => state.site_url,
                'templateList': state => state.templateList.templateListData,
                'commonTemplateData': state => state.templateList.commonTemplateData,
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'v1_import_flag': state => state.v1_import_flag
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'authActions': state => state.authActions,
                'authOperations': state => state.authOperations,
                'authResource': state => state.authResource,
                'projectName': state => state.projectName,
                'project_id': state => state.project_id
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
            this.getCollectList()
            this.getProjectBaseInfo()
            this.queryCreateCommonTplPerm()
            // this.getExpiredSubflowData() 公共流程暂时不显示子流程更新提示
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'addToCollectList',
                'deleteCollect',
                'loadCollectList'
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
            async queryCreateCommonTplPerm () {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: 'common_flow',
                        action_ids: JSON.stringify(['create'])
                    })
                    const hasCreatePerm = !!res.data.details.find(item => {
                        return item.action_id === 'create' && item.is_pass
                    })
                    if (hasCreatePerm) {
                        this.createCommonTplAction = ['create']
                    }
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            async getTemplateList () {
                this.listLoading = true
                try {
                    const { subprocessUpdateVal, creator, category, queryTime, flowName } = this.requestData
                    const has_subprocess = (subprocessUpdateVal === '' || subprocessUpdateVal === 0) ? undefined : (subprocessUpdateVal > 0)
                    const subprocess_has_update = subprocessUpdateVal === '' ? undefined : (subprocessUpdateVal !== 0)
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        common: '1',
                        pipeline_template__name__contains: flowName || undefined,
                        pipeline_template__creator__contains: creator || undefined,
                        category: category || undefined,
                        subprocess_has_update,
                        has_subprocess
                    }
                    if (queryTime[0] && queryTime[1]) {
                        data['pipeline_template__edit_time__gte'] = moment(queryTime[0]).format('YYYY-MM-DD')
                        data['pipeline_template__edit_time__lte'] = moment(queryTime[1]).add('1', 'd').format('YYYY-MM-DD')
                    }

                    const templateListData = await this.loadTemplateList(data)
                    const list = templateListData.objects
                    this.setTemplateListData({ list, isCommon: true })
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
            async getExpiredSubflowData () {
                try {
                    const resp = await this.getExpiredSubProcess()
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
                if (!this.hasPermission(this.createTplRequired, this.createCommonTplAction, this.tplOperations)) {
                    const resourceData = {
                        name: i18n.t('公共流程'),
                        id: '',
                        auth_actions: this.createCommonTplAction
                    }
                    this.applyForPermission(this.createTplRequired, resourceData, this.tplOperations, this.tplResource)
                } else {
                    this.$router.push({
                        name: 'commonTemplatePanel',
                        params: { type: 'new' }
                    })
                }
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.getTemplateList()
            },
            onSearchFormSubmit (data) {
                this.requestData = data
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
                        common: '1',
                        list
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
                        templateId: this.theDeleteTemplateId,
                        common: '1'
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
                    'edit': { name: 'commonTemplatePanel', params: { type: 'edit' } },
                    'newTemplate': { name: 'commonTemplatePanel', params: { type: 'new' } },
                    'newTask': { name: 'taskStep', params: { project_id: this.project_id, step: 'selectnode' } },
                    'clone': { name: 'commonTemplatePanel', params: { type: 'clone' } }
                }
                const url = urlMap[name]
                url.query = {
                    template_id,
                    common: '1'
                }
                if (name === 'newTask') {
                    this.$refs.ProjectSelectorModal.show(template_id)
                    return false
                }
                this.$router.push(url)
            },
            // 选完项目后新建任务
            selectedProjectToNewTask (projectId, templateId) {
                this.$router.push({
                    name: 'taskStep',
                    query: { template_id: templateId, common: '1' },
                    params: { project_id: projectId, step: 'selectnode' }
                })
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
                                template_id: template.template_id,
                                name: template.name,
                                id: template.id
                            },
                            category: 'common_flow'
                        }])
                        if (res.objects.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                    } else { // cancel
                        const delId = this.collectionList.find(m => m.extra_info.id === template.id && m.category === 'common_flow').id
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
                return !!this.collectionList.find(m => m.extra_info.id === id && m.category === 'common_flow')
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
a {
    cursor: pointer;
}
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
