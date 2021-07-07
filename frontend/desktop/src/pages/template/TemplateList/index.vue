/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="template-container">
        <skeleton :loading="firstLoading" loader="templateList">
            <div class="list-wrapper">
                <list-page-tips-title
                    :num="expiredSubflowTplList.length"
                    @viewClick="handleSubflowFilter">
                </list-page-tips-title>
                <advance-search-form
                    ref="advanceSearch"
                    id="templateList"
                    :open="isSearchFormOpen"
                    :search-form="searchForm"
                    :search-config="{ placeholder: $t('请输入流程名称') }"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            v-cursor="{ active: !hasPermission(['flow_create'], authActions) }"
                            theme="primary"
                            :class="['create-template-btn', {
                                'btn-permission-disable': !hasPermission(['flow_create'], authActions)
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
                <div class="template-table-content">
                    <bk-table
                        class="template-table"
                        :data="templateList"
                        :pagination="pagination"
                        :size="setting.size"
                        v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }"
                        @sort-change="handleSortChange"
                        @page-change="onPageChange"
                        @page-limit-change="onPageLimitChange">
                        <bk-table-column
                            v-for="item in setting.selectedFields"
                            :key="item.id"
                            :label="item.label"
                            :prop="item.id"
                            :width="item.width"
                            :min-width="item.min_width"
                            :render-header="renderTableHeader"
                            :sortable="item.sortable">
                            <template slot-scope="{ row }">
                                <!--流程名称-->
                                <div v-if="item.id === 'name'">
                                    <template>
                                        <a
                                            v-if="!hasPermission(['flow_view'], row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            @click="onTemplatePermissonCheck(['flow_view'], row)">
                                            {{row.name}}
                                        </a>
                                        <router-link
                                            v-else
                                            class="template-name"
                                            :title="row.name"
                                            :to="getJumpUrl('edit', row.id)">
                                            {{row.name}}
                                        </router-link>
                                    </template>
                                </div>
                                <div v-else-if="item.id === 'label'" class="label-column">
                                    <template v-if="row.template_labels && row.template_labels.length > 0">
                                        <span
                                            v-for="label in row.template_labels"
                                            class="label-name"
                                            :key="label.id"
                                            :style="{ background: label.color, color: darkColorList.includes(label.color) ? '#fff' : '#262e4f' }"
                                            @click="onSearchLabel(label.label_id)">
                                            {{ label.name }}
                                        </span>
                                    </template>
                                    <span v-else>--</span>
                                </div>
                                <!--子流程更新-->
                                <div v-else-if="item.id === 'subprocess_has_update'" :class="['subflow-update', { 'subflow-has-update': row.subprocess_has_update }]">
                                    {{getSubflowContent(row)}}
                                    <span v-if="!isFlowVisited(row.id) " class="red-dot"></span>
                                </div>
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="row[item.id]">{{ row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="240" class="operation-cell">
                            <template slot-scope="props">
                                <div class="template-operation">
                                    <template>
                                        <a
                                            v-if="!hasPermission(['flow_create_task'], props.row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            @click="onTemplatePermissonCheck(['flow_create_task'], props.row)">
                                            {{$t('新建任务')}}
                                        </a>
                                        <router-link
                                            v-else
                                            class="template-operate-btn"
                                            :to="getJumpUrl('newTask', props.row.id)">
                                            {{$t('新建任务')}}
                                        </router-link>
                                        <a
                                            v-if="!hasPermission(['flow_view'], props.row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            @click="onTemplatePermissonCheck(['flow_view'], props.row)">
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
                                            :tippy-options="{ boundary: 'window', duration: [0, 0] }"
                                            :on-show="onShowMoreOperation">
                                            <i class="bk-icon icon-more drop-icon-ellipsis"></i>
                                            <ul slot="content">
                                                <li class="opt-btn">
                                                    <a
                                                        v-cursor="{ active: !hasPermission(['flow_view'], props.row.auth_actions) }"
                                                        href="javascript:void(0);"
                                                        :class="{
                                                            'disable': collectingId === props.row.id || collectListLoading,
                                                            'text-permission-disable': !hasPermission(['flow_view'], props.row.auth_actions)
                                                        }"
                                                        @click="onCollectTemplate(props.row, $event)">
                                                        {{ isCollected(props.row.id) ? $t('取消收藏') : $t('收藏') }}
                                                    </a>
                                                </li>
                                                <li class="opt-btn">
                                                    <a
                                                        v-if="!hasPermission(['flow_edit'], props.row.auth_actions)"
                                                        v-cursor
                                                        class="text-permission-disable"
                                                        @click="onTemplatePermissonCheck(['flow_edit'], props.row)">
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
                                                        v-cursor="{ active: !hasPermission(['flow_delete'], props.row.auth_actions) }"
                                                        href="javascript:void(0);"
                                                        :class="{
                                                            'text-permission-disable': !hasPermission(['flow_delete'], props.row.auth_actions)
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
        <ImportTemplateDialog
            :auth-actions="authActions"
            :is-import-dialog-show="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportTemplateDialog>
        <ExportTemplateDialog
            :is-export-dialog-show="isExportDialogShow"
            :project-info-loading="projectInfoLoading"
            :pending="pending.export"
            :project_id="project_id"
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
            <div class="dialog-content" v-bkloading="{ isLoading: pending.delete, opacity: 1, zIndex: 100 }">
                {{$t('确认删除') + '"' + deleteTemplateName + '"' + '?' }}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { DARK_COLOR_LIST } from '@/constants/index.js'
    import tools from '@/utils/tools.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import ImportTemplateDialog from './ImportTemplateDialog.vue'
    import ExportTemplateDialog from './ExportTemplateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    import ListPageTipsTitle from '../ListPageTipsTitle.vue'

    const categoryTips = i18n.t('模板分类即将下线，建议使用标签')

    const SEARCH_FORM = [
        {
            type: 'select',
            key: 'label_ids',
            multiple: true,
            label: i18n.t('标签'),
            placeholder: i18n.t('请选择标签'),
            list: [],
            value: []
        },
        {
            type: 'dateRange',
            key: 'queryTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('更新时间'),
            value: ['', '']
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
        },
        {
            type: 'select',
            label: i18n.t('分类'),
            key: 'category',
            loading: false,
            placeholder: i18n.t('请选择分类'),
            tips: categoryTips,
            list: [],
            value: ''
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
            width: 80
        },
        {
            id: 'name',
            label: i18n.t('流程名称'),
            disabled: true,
            min_width: 400
        },
        {
            id: 'label',
            label: i18n.t('标签'),
            min_width: 300
        },
        {
            id: 'create_time',
            label: i18n.t('创建时间'),
            sortable: 'custom',
            width: 200
        },
        {
            id: 'edit_time',
            label: i18n.t('更新时间'),
            sortable: 'custom',
            width: 200
        },
        {
            id: 'subprocess_has_update',
            label: i18n.t('子流程更新'),
            width: 180
        },
        {
            id: 'category_name',
            label: i18n.t('分类'),
            min_width: 180
        },
        {
            id: 'creator_name',
            label: i18n.t('创建人'),
            width: 160
        },
        {
            id: 'editor_name',
            label: i18n.t('更新人'),
            width: 160
        }
    ]

    export default {
        name: 'TemplateList',
        components: {
            Skeleton,
            ImportTemplateDialog,
            ExportTemplateDialog,
            ListPageTipsTitle,
            AdvanceSearchForm,
            NoData
        },
        mixins: [permission],
        props: {
            project_id: [String, Number],
            page: [String, Number],
            limit: [String, Number]
        },
        data () {
            const {
                page = 1,
                limit = 15,
                category = '',
                queryTime = '',
                subprocessUpdateVal = '',
                creator = '',
                keyword = '',
                label_ids = ''
            } = this.$route.query
            const searchForm = SEARCH_FORM.map(item => {
                if (this.$route.query[item.key]) {
                    if (Array.isArray(item.value)) {
                        const value = this.$route.query[item.key].split(',')
                        item.value = item.key === 'label_ids' ? value.map(v => Number(v)) : value
                    } else {
                        item.value = this.$route.query[item.key]
                    }
                }
                return item
            })
            if (this.$route.query.id__in !== '') {
                for (let index = 0; index < searchForm.length; index++) {
                    if (searchForm[index].key === 'subprocessUpdateVal') {
                        searchForm[index].value = '1'
                    }
                }
            }
            const isSearchFormOpen = SEARCH_FORM.some(item => this.$route.query[item.key])
            return {
                firstLoading: true,
                listLoading: false,
                projectInfoLoading: true, // 模板分类信息 loading
                searchStr: '',
                searchForm,
                isSearchFormOpen, // 高级搜索表单默认展开
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
                    category,
                    creator,
                    subprocessUpdateVal: subprocessUpdateVal !== '' ? Number(subprocessUpdateVal) : '',
                    queryTime: queryTime ? queryTime.split(',') : ['', ''],
                    label_ids: label_ids ? label_ids.split(',') : [],
                    flowName: keyword
                },
                totalPage: 1,
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                collectingId: '', // 正在被收藏/取消收藏的模板id
                collectListLoading: false,
                collectionList: [],
                ordering: null, // 排序参数
                darkColorList: DARK_COLOR_LIST,
                tableFields: TABLE_FIELDS,
                defaultSelected: ['id', 'name', 'label', 'edit_time', 'subprocess_has_update', 'creator_name'],
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: [],
                    size: 'small'
                },
                categoryTips
            }
        },
        computed: {
            ...mapState({
                'site_url': state => state.site_url,
                'templateList': state => state.templateList.templateListData,
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'v1_import_flag': state => state.v1_import_flag,
                'username': state => state.username
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'authActions': state => state.authActions,
                'projectName': state => state.projectName
            })
        },
        watch: {
            page (val, oldVal) {
                if (val !== oldVal) {
                    this.pagination.current = Number(val) || 1
                    this.getTemplateList()
                }
            }
        },
        async created () {
            this.getFields()
            this.getProjectBaseInfo()
            this.getProjectLabelList()
            this.getExpiredSubflowData()
            this.getCollectList()
            this.onSearchInput = tools.debounce(this.searchInputhandler, 500)
            await this.getTemplateList()
            this.firstLoading = false
            this.isSearchFormOpen = this.$route.query.id__in !== ''
        },
        beforeRouteLeave (to, from, next) {
            // 记录访问过的流程 id
            if (to.name === 'templatePanel' && to.query.template_id) {
                this.pushToVisitedFlow(to.query.template_id)
            }
            next()
        },
        methods: {
            ...mapActions([
                'loadCollectList',
                'addToCollectList',
                'deleteCollect'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList',
                'deleteTemplate',
                'templateImport',
                'templateExport',
                'getExpiredSubProcess'
            ]),
            ...mapActions('project/', [
                'getProjectLabelsWithDefault'
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
                    const { subprocessUpdateVal, creator, category, queryTime, flowName, label_ids } = this.requestData

                    /**
                     * 无子流程 has_subprocess=false
                     * 有子流程，需要更新 has_subprocess=true&subprocess_has_update=true
                     * 有子流程，不需要更新 has_subprocess=true&subprocess_has_update=false
                     * 不做筛选 has_subprocess=undefined
                     */
                    const has_subprocess = (subprocessUpdateVal === 1 || subprocessUpdateVal === -1) ? true : (subprocessUpdateVal === 0 ? false : undefined)
                    const subprocess_has_update = subprocessUpdateVal === 1 ? true : (subprocessUpdateVal === -1 ? false : undefined)
                    const data = {
                        project__id: this.project_id,
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        pipeline_template__name__icontains: flowName || undefined,
                        pipeline_template__creator__contains: creator || undefined,
                        category: category || undefined,
                        label_ids: label_ids && label_ids.length ? label_ids.join(',') : undefined,
                        subprocess_has_update,
                        has_subprocess,
                        id__in: this.$route.query.id__in || undefined,
                        order_by: this.ordering || undefined
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
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('templateList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size
                    selectedFields = fieldList
                } else {
                    selectedFields = this.defaultSelected
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
            },
            async getProjectBaseInfo () {
                this.projectInfoLoading = true
                this.categoryLoading = true
                const form = this.searchForm.find(item => item.key === 'category')
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.setProjectBaseInfo(res.data)
                    form.list = res.data.task_categories
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectInfoLoading = false
                    form.loading = false
                }
            },
            async getExpiredSubflowData () {
                try {
                    const resp = await this.getExpiredSubProcess({ project__id: this.project_id })
                    if (resp.result) {
                        this.expiredSubflowTplList = resp.data
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getCollectList () {
                try {
                    this.collectListLoading = true
                    const res = await this.loadCollectList()
                    this.collectionList = res.objects
                } catch (e) {
                    console.log(e)
                } finally {
                    this.collectListLoading = false
                }
            },
            async getProjectLabelList () {
                const form = this.searchForm.find(item => item.key === 'label_ids')
                try {
                    this.templateLabelLoading = true
                    const res = await this.getProjectLabelsWithDefault(this.project_id)
                    form.list = res.data.map(item => Object.assign({}, item, { value: item.id }))
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLabelLoading = false
                    form.loading = false
                }
            },
            onShowMoreOperation () {
                window.reportInfo({
                    page: 'templateList',
                    zone: 'tableMoreOperation',
                    event: 'hover'
                })
            },
            checkCreatePermission () {
                if (!this.hasPermission(['flow_create'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['flow_create'], this.authActions, resourceData)
                } else {
                    this.$router.push({
                        name: 'templatePanel',
                        params: { type: 'new', project_id: this.project_id }
                    })
                }
            },
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
                this.pagination.current = 1
                this.updateUrl()
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
                    const resp = await this.templateExport({ list })
                    if (resp.result) {
                        this.isExportDialogShow = false
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.export = false
                }
            },
            onExportCancel () {
                this.isExportDialogShow = false
            },
            onDeleteTemplate (template) {
                if (!this.hasPermission(['flow_delete'], template.auth_actions)) {
                    this.onTemplatePermissonCheck(['flow_delete'], template)
                    return
                }
                this.theDeleteTemplateId = template.id
                this.deleteTemplateName = template.name
                this.isDeleteDialogShow = true
            },
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('templateList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            handleSortChange ({ prop, order }) {
                const params = 'pipeline_template__' + prop
                if (order === 'ascending') {
                    this.ordering = params
                } else if (order === 'descending') {
                    this.ordering = '-' + params
                } else {
                    this.ordering = ''
                }
                this.pagination.current = 1
                this.getTemplateList()
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property !== 'category_name') {
                    return column.label
                }

                return h('span', {
                    'class': 'category-label'
                }, [
                    column.label,
                    h('i', {
                        'class': 'common-icon-info table-header-tips',
                        directives: [{
                            name: 'bk-tooltips',
                            value: this.categoryTips
                        }]
                    })
                ])
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getTemplateList()
            },
            onPageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { category, queryTime, subprocessUpdateVal, creator, label_ids, flowName } = this.requestData
                const filterObj = {
                    limit,
                    category,
                    subprocessUpdateVal,
                    creator,
                    page: current,
                    queryTime: queryTime.every(item => item) ? queryTime.join(',') : '',
                    label_ids: label_ids.length ? label_ids.join(',') : '',
                    keyword: flowName
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.push({ name: 'process', params: { project_id: this.project_id }, query })
            },
            /**
             * 单个模板操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 模板数据对象
             */
            onTemplatePermissonCheck (required, template) {
                const project = {
                    id: this.project_id,
                    name: this.projectName
                }
                this.applyForPermission(required, this.authActions, { flow: [template], project: [project] })
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
                    console.log(e)
                } finally {
                    this.pending.delete = false
                }
            },
            onDeleteCancel () {
                this.theDeleteTemplateId = undefined
                this.isDeleteDialogShow = false
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
                    'newTask': { name: 'taskCreate', params: { project_id: this.project_id, step: 'selectnode' } },
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
                    query: { template_id: id, template_source: 'project' }
                }
            },
            // 获得表格中“子流程更新”列展示内容
            getSubflowContent (item) {
                if (!item.has_subprocess) {
                    return '--'
                }
                return item.subprocess_has_update ? i18n.t('待更新') : i18n.t('否')
            },
            // 标题提示信息，查看子流程更新
            handleSubflowFilter () {
                const searchComp = this.$refs.advanceSearch
                searchComp.onAdvanceOpen(true)
                searchComp.onChangeFormItem(1, 'subprocessUpdateVal')
                searchComp.submit()
            },
            // 筛选包含当前标签的模板
            onSearchLabel (id) {
                const searchComp = this.$refs.advanceSearch
                searchComp.onAdvanceOpen(true)
                searchComp.onChangeFormItem([id], 'label_ids')
                searchComp.submit()
            },
            // 添加/取消收藏模板
            async onCollectTemplate (template) {
                if (!this.hasPermission(['flow_view'], template.auth_actions)) {
                    this.onTemplatePermissonCheck(['flow_view'], template)
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
                    console.log(e)
                } finally {
                    this.collectingId = ''
                }
            },
            // 判断是否已在收藏列表
            isCollected (id) {
                return !!this.collectionList.find(m => m.extra_info.id === id && m.category === 'flow')
            },
            // 缓存记录访问过的流程 id
            pushToVisitedFlow (id) {
                const saveId = `${this.username}_${this.project_id}_${id}`
                const visitedStr = sessionStorage.getItem('visitedFlow')
                const visitedList = visitedStr ? JSON.parse(visitedStr) : []
                if (!visitedList.some(item => item === saveId)) {
                    visitedList.push(saveId)
                    sessionStorage.setItem('visitedFlow', JSON.stringify(visitedList))
                }
            },
            // 判断流程是否访问过
            isFlowVisited (id) {
                const saveId = `${this.username}_${this.project_id}_${id}`
                const visitedStr = sessionStorage.getItem('visitedFlow')
                if (visitedStr) {
                    const visitedList = JSON.parse(visitedStr)
                    return visitedList.some(item => item === saveId)
                }
                return false
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.template-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;
    @include scrollbar;
}
.create-template-btn {
    min-width: 120px;
}
.dialog-content {
    padding: 30px;
    word-break: break-all;
}
.template-table-content {
    background: #ffffff;
    a.template-name {
        color: $blueDefault;
    }
    .label-column {
        display: table-cell;
    }
    .label-name {
        display: inline-block;
        margin: 4px 0 4px 4px;
        padding: 2px 6px;
        font-size: 12px;
        line-height: 1;
        color: #63656e;
        border-radius: 8px;
        cursor: pointer;
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
        .red-dot {
            margin-left: 3px;
            display: inline-block;
            width: 6px;
            height: 6px;
            background: #ff5757;
            border-radius: 50%;
            vertical-align: 1px;
        }
    }
    /deep/.table-header-tips {
        margin-left: 4px;
        font-size: 14px;
        color: #c4c6cc;
        cursor: pointer;
    }
}
</style>
