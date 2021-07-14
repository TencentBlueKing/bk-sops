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
                <advance-search-form
                    ref="advanceSearch"
                    id="commonTplList"
                    :open="isSearchFormOpen"
                    :search-form="searchForm"
                    :search-config="{ placeholder: $t('请输入流程名称') }"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            v-cursor="{ active: !hasCreateCommonTplPerm }"
                            theme="primary"
                            style="min-width: 120px;"
                            :class="{
                                'btn-permission-disable': !hasCreateCommonTplPerm
                            }"
                            @click="checkCreatePermission">
                            {{$t('新建')}}
                        </bk-button>
                        <bk-dropdown-menu style="margin-left: 20px;">
                            <div class="import-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('导入') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="import-option-list" slot="dropdown-content">
                                <li @click="isImportDialogShow = true">{{ $t('导入') }}DAT{{ $t('文件') }}</li>
                                <li @click="isImportYamlDialogShow = true">{{ $t('导入') }}YAML{{ $t('文件') }}</li>
                            </ul>
                        </bk-dropdown-menu>
                        <bk-dropdown-menu style="margin-left: 14px;">
                            <div class="export-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('批量操作') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="batch-operation-list" slot="dropdown-content">
                                <li @click="onExportTemplate('dat')">{{ $t('导出为') }}DAT</li>
                                <li @click="onExportTemplate('yaml')">{{ $t('导出为') }}YAML</li>
                                <li :class="{ 'disabled': selectedTpls.length === 0 }" @click="onBatchCollect">{{ $t('收藏') }}</li>
                                <li :class="{ 'disabled': selectedTpls.length === 0 }" @click="onBatchDelete">{{ $t('删除') }}</li>
                            </ul>
                        </bk-dropdown-menu>
                        <div v-if="selectedTpls.length > 0" class="selected-tpl-num">
                            {{ $t('已选择') }}{{ selectedTpls.length }}{{ $t('项') }}
                            <bk-link theme="primary" @click="selectedTpls = []">{{ $t('清空') }}</bk-link>
                        </div>
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
                        <bk-table-column width="70" :render-header="renderHeaderCheckbox">
                            <template slot-scope="props">
                                <bk-checkbox :value="!!selectedTpls.find(tpl => tpl.id === props.row.id)" @change="onToggleTplItem($event, props.row)"></bk-checkbox>
                            </template>
                        </bk-table-column>
                        <bk-table-column
                            v-for="item in setting.selectedFields"
                            :key="item.id"
                            :label="item.label"
                            :prop="item.id"
                            :width="item.width"
                            :min-width="item.min_width"
                            :sortable="item.sortable">
                            <template slot-scope="{ row }">
                                <!--流程名称-->
                                <div v-if="item.id === 'name'" class="name-column">
                                    <a
                                        v-if="!hasPermission(['common_flow_view'], row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissonCheck(['common_flow_view'], row)">
                                        {{row.name}}
                                    </a>
                                    <a
                                        v-else
                                        class="template-name"
                                        :title="row.name"
                                        @click.prevent="getJumpUrl('edit', row.id)">
                                        {{row.name}}
                                    </a>
                                </div>
                                <!--子流程更新-->
                                <div v-else-if="item.id === 'subprocess_has_update'" :class="['subflow-update', { 'subflow-has-update': row.subprocess_has_update }]">
                                    {{getSubflowContent(row)}}
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
                                            class="template-operate-btn"
                                            @click.prevent="handleCreateTaskClick(props.row)">
                                            {{$t('新建任务')}}
                                        </a>
                                        <a
                                            v-if="!hasPermission(['common_flow_view'], props.row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            @click="onTemplatePermissonCheck(['common_flow_view'], props.row)">
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
                                                        v-cursor="{ active: !hasPermission(['common_flow_view'], props.row.auth_actions) }"
                                                        href="javascript:void(0);"
                                                        :class="{
                                                            'disable': collectingId === props.row.id || collectListLoading,
                                                            'text-permission-disable': !hasPermission(['common_flow_view'], props.row.auth_actions)
                                                        }"
                                                        @click="onCollectTemplate(props.row, $event)">
                                                        {{ isCollected(props.row.id) ? $t('取消收藏') : $t('收藏') }}
                                                    </a>
                                                </li>
                                                <li class="opt-btn">
                                                    <a
                                                        v-if="!hasPermission(['common_flow_edit'], props.row.auth_actions)"
                                                        v-cursor
                                                        class="text-permission-disable"
                                                        @click="onTemplatePermissonCheck(['common_flow_edit'], props.row)">
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
                                                        v-cursor="{ active: !hasPermission(['common_flow_delete'], props.row.auth_actions) }"
                                                        href="javascript:void(0);"
                                                        :class="{
                                                            'text-permission-disable': !hasPermission(['common_flow_delete'], props.row.auth_actions)
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
        <ImportDatTplDialog
            common="1"
            :has-create-common-tpl-perm="hasCreateCommonTplPerm"
            :is-import-dialog-show="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportDatTplDialog>
        <ImportYamlTplDialog
            common="1"
            :project_id="project_id"
            :is-show.sync="isImportYamlDialogShow"
            @confirm="onImportYamlSuccess">
        </ImportYamlTplDialog>
        <ExportTemplateDialog
            common="1"
            :is-export-dialog-show.sync="isExportDialogShow"
            :selected="selectedTpls"
            :type="exportType">
        </ExportTemplateDialog>
        <SelectProjectModal
            :title="$t('创建任务')"
            :show="isSelectProjectShow"
            :confirm-loading="permissionLoading"
            :confirm-cursor="!hasCreateTaskPerm"
            @onChange="handleProjectChange"
            @onConfirm="handleCreateTaskConfirm"
            @onCancel="handleCreateTaskCancel">
        </SelectProjectModal>
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
    import toolsUtils from '@/utils/tools.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import ImportDatTplDialog from '../TemplateList/ImportDatTplDialog.vue'
    import ImportYamlTplDialog from '../TemplateList/ImportYamlTplDialog.vue'
    import ExportTemplateDialog from '../TemplateList/ExportTemplateDialog.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import SelectProjectModal from '@/components/common/modal/SelectProjectModal.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'

    const SEARCH_FORM = [
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
        },
        {
            type: 'select',
            label: i18n.t('分类'),
            key: 'category',
            loading: true,
            placeholder: i18n.t('请选择分类'),
            tips: i18n.t('模板分类即将下线，建议使用标签'),
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
            width: 200
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
            ImportDatTplDialog,
            ImportYamlTplDialog,
            ExportTemplateDialog,
            SelectProjectModal,
            AdvanceSearchForm,
            NoData
        },
        mixins: [permission],
        data () {
            const {
                page = 1,
                limit = 15,
                category = '',
                queryTime = '',
                subprocessUpdateVal = '',
                creator = '',
                keyword = ''
            } = this.$route.query
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
                listLoading: false,
                projectInfoLoading: true, // 模板分类信息 loading
                searchForm,
                isSearchFormOpen,
                exportType: 'dat', // 模板导出类型
                expiredSubflowTplList: [],
                selectedTpls: [], // 选中的流程模板
                templateList: [],
                isDeleteDialogShow: false,
                isImportDialogShow: false,
                isImportYamlDialogShow: false,
                isExportDialogShow: false,
                isAuthorityDialogShow: false,
                isSelectProjectShow: false,
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
                    category,
                    subprocessUpdateVal: subprocessUpdateVal !== '' ? Number(subprocessUpdateVal) : '',
                    creator,
                    queryTime: queryTime ? queryTime.split(',') : ['', ''],
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
                hasCreateCommonTplPerm: false, // 创建公共流程权限
                permissionLoading: false,
                hasCreateTaskPerm: true,
                selectedProject: {},
                selectedTpl: {},
                ordering: null, // 排序参数
                tableFields: TABLE_FIELDS,
                defaultSelected: ['id', 'name', 'label', 'edit_time', 'subprocess_has_update', 'creator_name'],
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                }
            }
        },
        computed: {
            ...mapState({
                'site_url': state => state.site_url,
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'v1_import_flag': state => state.v1_import_flag,
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'projectName': state => state.projectName,
                'project_id': state => state.project_id
            }),
            crtPageSelectedAll () {
                return this.templateList.length > 0 && this.templateList.every(item => this.selectedTpls.find(tpl => tpl.id === item.id))
            }
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
            this.getCollectList()
            this.getProjectBaseInfo()
            this.queryCreateCommonTplPerm()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
            await this.getTemplateList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'addToCollectList',
                'deleteCollect',
                'loadCollectList'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList',
                'deleteTemplate',
                'templateImport',
                'batchDeleteTpl'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async queryCreateCommonTplPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'common_flow_create'
                    })
                    this.hasCreateCommonTplPerm = res.data.is_allow
                } catch (e) {
                    console.log(e)
                }
            },
            async getTemplateList () {
                this.listLoading = true
                try {
                    const data = this.getQueryData()
                    const templateListData = await this.loadTemplateList(data)
                    this.templateList = templateListData.objects
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
            getQueryData () {
                const { subprocessUpdateVal, creator, category, queryTime, flowName } = this.requestData
                /**
                 * 无子流程 has_subprocess=false
                 * 有子流程，需要更新 has_subprocess=true&subprocess_has_update=true
                 * 有子流程，不需要更新 has_subprocess=true&subprocess_has_update=false
                 * 不做筛选 has_subprocess=undefined
                 */
                const has_subprocess = (subprocessUpdateVal === 1 || subprocessUpdateVal === -1) ? true : (subprocessUpdateVal === 0 ? false : undefined)
                const subprocess_has_update = subprocessUpdateVal === 1 ? true : (subprocessUpdateVal === -1 ? false : undefined)
                const data = {
                    limit: this.pagination.limit,
                    offset: (this.pagination.current - 1) * this.pagination.limit,
                    common: '1',
                    pipeline_template__name__icontains: flowName || undefined,
                    pipeline_template__creator__contains: creator || undefined,
                    category: category || undefined,
                    subprocess_has_update,
                    has_subprocess,
                    order_by: this.ordering || undefined
                }
                if (queryTime[0] && queryTime[1]) {
                    data['pipeline_template__edit_time__gte'] = moment(queryTime[0]).format('YYYY-MM-DD')
                    data['pipeline_template__edit_time__lte'] = moment(queryTime[1]).add('1', 'd').format('YYYY-MM-DD')
                }
                return data
            },
            async getProjectBaseInfo () {
                this.projectInfoLoading = true
                this.categoryLoading = true
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.setProjectBaseInfo(res.data)
                    this.templateCategoryList = res.data.task_categories
                    const form = this.searchForm.find(item => item.key === 'category')
                    form.list = this.templateCategoryList
                    form.loading = false
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectInfoLoading = false
                    this.categoryLoading = false
                }
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('commonTemplateList')
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
            checkCreatePermission () {
                if (!this.hasCreateCommonTplPerm) {
                    this.applyForPermission(['common_flow_create'])
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
                this.requestData = Object.assign({}, this.requestData, data)
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
            },
            renderHeaderCheckbox (h) {
                const self = this
                return h('div', {
                    'class': {
                        'select-all-cell': true,
                        'full-selected': this.pagination.count === this.selectedTpls.length
                    }
                }, [
                    h('bk-checkbox', {
                        props: {
                            value: this.crtPageSelectedAll
                        },
                        on: {
                            change: function (val) {
                                self.onToggleTplAll(val)
                            }
                        }
                    }),
                    h('bk-popover', {
                        props: {
                            placement: 'bottom',
                            theme: 'light',
                            distance: 0,
                            'tippy-options': {
                                hideOnClick: false
                            },
                            'ext-cls': 'select-all-tpl-popover'
                        }
                    }, [
                        h('i', {
                            'class': 'bk-icon icon-angle-down'
                        }),
                        h('div', {
                            slot: 'content'
                        }, [
                            h('div', {
                                'class': 'mode-item',
                                on: {
                                    click: function () {
                                        self.onSeleteTplAll('current')
                                    }
                                }
                            }, [i18n.t('本页全选')]),
                            h('div', {
                                'class': 'mode-item',
                                on: {
                                    click: function () {
                                        self.onSeleteTplAll('full')
                                    }
                                }
                            }, [i18n.t('跨页全选')])
                        ])
                    ])
                ])
            },
            // 本页全选、取消本页/跨页全选
            onToggleTplAll (val) {
                if (val) {
                    this.onSeleteTplAll('current')
                } else {
                    if (this.selectedTpls.length === this.pagination.count) {
                        this.selectedTpls = []
                    } else {
                        this.templateList.forEach(tpl => {
                            const index = this.selectedTpls.findIndex(item => item.id === tpl.id)
                            this.selectedTpls.splice(index, 1)
                        })
                    }
                }
            },
            // 本页全选、跨页全选
            async onSeleteTplAll (type) {
                if (type === 'full') {
                    const data = this.getQueryData()
                    data.limit = 0
                    data.offset = 0
                    const res = await this.loadTemplateList(data)
                    this.selectedTpls = res.objects.slice(0)
                } else {
                    this.templateList.forEach(item => {
                        if (!this.selectedTpls.find(tpl => tpl.id === item.id)) {
                            this.selectedTpls.push(item)
                        }
                    })
                }
            },
            onToggleTplItem (val, tpl) {
                if (val) {
                    this.selectedTpls.push(tpl)
                } else {
                    const index = this.selectedTpls.findIndex(item => item.id === tpl.id)
                    this.selectedTpls.splice(index, 1)
                }
            },
            async onBatchCollect () {
                if (this.selectedTpls.length === 0) {
                    return
                }
                this.batchCollectPending = true
                try {
                    const data = this.selectedTpls.filter(tpl => !this.isCollected(tpl.id)).map(tpl => {
                        return {
                            extra_info: {
                                template_id: tpl.id,
                                name: tpl.name,
                                id: tpl.id
                            },
                            category: 'common_flow'
                        }
                    })
                    if (data.length === 0) {
                        return
                    }
                    const res = await this.addToCollectList(data)
                    this.getCollectList()
                    if (res.objects.length) {
                        this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.batchCollectPending = false
                }
            },
            onBatchDelete () {
                if (this.selectedTpls.length === 0 || this.batchDeletePending) {
                    return
                }
                this.$bkInfo({
                    type: 'warning',
                    title: `${i18n.t('确认删除所选的')}${this.selectedTpls.length}${i18n.t('项流程吗')}`,
                    confirmFn: this.batchDeleteConfirm
                })
            },
            async batchDeleteConfirm () {
                const data = {
                    common: true,
                    projectId: this.project_id,
                    ids: this.selectedTpls.map(tpl => tpl.id)
                }
                const res = await this.batchDeleteTpl(data)
                if (res.result) {
                    if (Array.isArray(res.data.success) && res.data.success.length > 0) {
                        res.data.success.forEach(id => {
                            const index = this.selectedTpls.findIndex(tpl => tpl.id === id)
                            this.selectedTpls.splice(index, 1)
                        })
                        this.pagination.current = 1
                        this.getTemplateList()
                    }
                }
                return Promise.resolve()
            },
            onImportTemplate () {
                this.isImportDialogShow = true
            },
            onImportConfirm () {
                this.isImportDialogShow = false
                this.getTemplateList()
            },
            onImportYamlSuccess () {
                this.isImportYamlDialogShow = false
                this.getTemplateList()
            },
            onImportCancel () {
                this.isImportDialogShow = false
            },
            onExportTemplate (type) {
                this.exportType = type
                this.isExportDialogShow = true
            },
            onDeleteTemplate (template) {
                if (!this.hasPermission(['common_flow_delete'], template.auth_actions)) {
                    this.onTemplatePermissonCheck(['common_flow_delete'], template)
                    return
                }
                this.theDeleteTemplateId = template.id
                this.deleteTemplateName = template.name
                this.isDeleteDialogShow = true
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
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('commonTemplateList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { category, queryTime, subprocessUpdateVal, creator, flowName } = this.requestData
                const filterObj = {
                    limit,
                    category,
                    subprocessUpdateVal,
                    creator,
                    page: current,
                    queryTime: queryTime.every(item => item) ? queryTime.join(',') : '',
                    keyword: flowName
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.push({ name: 'commonProcessList', query })
            },
            /**
             * 单个模板操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 模板数据对象
             */
            onTemplatePermissonCheck (required, template) {
                const curPermission = template.auth_actions.slice(0)
                const permissionData = {
                    common_flow: [{
                        id: template.id,
                        name: template.name
                    }]
                }
                this.applyForPermission(required, curPermission, permissionData)
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
                    if (this.selectedTpls.find(tpl => tpl.id === this.theDeleteTemplateId)) {
                        const index = this.selectedTpls.findIndex(tpl => tpl.id === this.theDeleteTemplateId)
                        this.selectedTpls.splice(index, 1)
                    }
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
                    'edit': { name: 'commonTemplatePanel', params: { type: 'edit' } },
                    'newTemplate': { name: 'commonTemplatePanel', params: { type: 'new' } },
                    'newTask': { name: 'taskCreate', params: { project_id: this.project_id, step: 'selectnode' } },
                    'clone': { name: 'commonTemplatePanel', params: { type: 'clone' } }
                }
                const url = urlMap[name]
                url.query = {
                    template_id,
                    common: '1'
                }
                this.$router.push(url)
            },
            getExecuteHistoryUrl (id) {
                return {
                    name: 'taskList',
                    params: { project_id: this.project_id },
                    query: { template_id: id, template_source: 'common' }
                }
            },
            // 获得子流程展示内容
            getSubflowContent (item) {
                if (!item.has_subprocess) {
                    return '--'
                }
                return item.subprocess_has_update ? i18n.t('是') : i18n.t('否')
            },
            // 添加/取消收藏模板
            async onCollectTemplate (template) {
                if (!this.hasPermission(['common_flow_view'], template.auth_actions)) {
                    this.onTemplatePermissonCheck(['common_flow_view'], template)
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
                    console.log(e)
                } finally {
                    this.collectingId = ''
                }
            },
            // 判断是否已在收藏列表
            isCollected (id) {
                return !!this.collectionList.find(m => m.extra_info.id === id && m.category === 'common_flow')
            },

            // 点击创建任务
            handleCreateTaskClick (tpl) {
                this.selectedTpl = tpl
                this.isSelectProjectShow = true
                this.permissionLoading = false
                this.hasCreateTaskPerm = true
            },
            async handleProjectChange (project) {
                try {
                    this.permissionLoading = false
                    this.selectedProject = project
                    const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                    const data = {
                        action: 'common_flow_create_task',
                        resources: [
                            {
                                system: bkSops.id,
                                type: 'project',
                                id: this.selectedProject.id,
                                attributes: {}
                            },
                            {
                                system: bkSops.id,
                                type: 'common_flow',
                                id: this.selectedTpl.id,
                                attributes: {}
                            }
                        ]
                    }
                    const resp = await this.queryUserPermission(data)
                    this.hasCreateTaskPerm = resp.data.is_allow
                } catch (e) {
                    console.log(e)
                } finally {
                    this.permissionLoading = false
                }
            },
            handleCreateTaskConfirm () {
                if (!this.hasCreateTaskPerm) {
                    const reqPerimmison = ['common_flow_create_task']
                    const curPermission = [...this.selectedTpl.auth_actions, ...this.selectedProject.auth_actions]
                    const resourceData = {
                        common_flow: [{
                            id: this.selectedTpl.id,
                            name: this.selectedTpl.name
                        }],
                        project: [{
                            id: this.selectedProject.id,
                            name: this.selectedProject.name
                        }]
                    }
                    this.applyForPermission(reqPerimmison, curPermission, resourceData)
                } else {
                    this.$router.push({
                        name: 'taskCreate',
                        query: { template_id: this.selectedTpl.id, common: '1' },
                        params: { project_id: this.selectedProject.id, step: 'selectnode' }
                    })
                }
            },
            handleCreateTaskCancel () {
                this.selectedTpl = {}
                this.selectedProject = {}
                this.isSelectProjectShow = false
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
a {
    cursor: pointer;
}
.dialog-content {
    padding: 30px;
    word-break: break-all;
}
.export-tpl-btn,
.import-tpl-btn {
    position: relative;
    display: flex;
    align-items: center;
    padding: 0 4px 0 20px;
    height: 32px;
    line-height: 32px;
    min-width: 88px;
    text-align: center;
    font-size: 14px;
    background: #ffffff;
    border: 1px solid #c4c6cc;
    border-radius: 3px;
    cursor: pointer;
    .bk-icon {
        font-size: 24px;
        transition: ease-in-out 0.4s;
    }
}
.bk-dropdown-menu{
    &:hover {
        .export-tpl-btn,
        .import-tpl-btn {
            border-color: #979ba5;
            .bk-icon {
                transform: rotate(180deg);
            }
        }
    }
    /deep/.bk-dropdown-content {
        z-index: 1;
    }
}
.batch-operation-list,
.import-option-list {
    & > li {
        padding: 0 10px;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        text-align: left;
        white-space: nowrap;
        background: #ffffff;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            background: #f4f6fa;
        }
        &.disabled {
            color: #cccccc;
            cursor: not-allowed;
        }
    }
}
.selected-tpl-num {
    margin-left: 10px;
    font-size: 12px;
    line-height: 1;
    /deep/.bk-link-text {
        margin-left: 6px;
        font-size: 12px;
        line-height: 1;
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
    /deep/.select-all-cell {
        display: flex;
        align-items: center;
        &.full-selected {
            .bk-form-checkbox {
                .bk-checkbox {
                    background: #ffffff;
                    &:after {
                        border-color: #3a84ff;
                    }
                }
            }
        }
        .icon-angle-down {
            margin-left: 2px;
            font-size: 18px;
            color: #979ba5;
        }
    }
}
</style>
