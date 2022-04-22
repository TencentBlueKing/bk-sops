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
                        <template>
                            <bk-button
                                v-cursor="{ active: !hasPermission(['flow_create'], authActions) }"
                                theme="primary"
                                :class="['create-template-btn', {
                                    'btn-permission-disable': !hasPermission(['flow_create'], authActions)
                                }]"
                                data-test-id="process_form_creatProcess"
                                @click="checkCreatePermission">
                                {{$t('新建')}}
                            </bk-button>
                            <bk-dropdown-menu style="margin: 0 14px;">
                                <div class="import-tpl-btn" slot="dropdown-trigger">
                                    <span>{{ $t('导入') }}</span>
                                    <i :class="['bk-icon icon-angle-down']"></i>
                                </div>
                                <ul class="import-option-list" slot="dropdown-content">
                                    <li data-test-id="process_list_importDatFile" @click="isImportDialogShow = true">{{ $t('导入') }}DAT{{ $t('文件') }}</li>
                                    <li data-test-id="process_list_importYamlFile" @click="isImportYamlDialogShow = true">{{ $t('导入') }}YAML{{ $t('文件') }}</li>
                                </ul>
                            </bk-dropdown-menu>
                        </template>
                        <bk-dropdown-menu>
                            <div class="export-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('批量操作') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="batch-operation-list" slot="dropdown-content">
                                <template v-for="operate in operateList">
                                    <li
                                        :key="operate.type"
                                        v-bk-tooltips="{
                                            content: operate.content,
                                            disabled: !selectedTpls.length || (operate.isOther ? hasBatchEditAuth : hasBatchViewAuth) }"
                                        :class="{ 'disabled': operate.isOther ? !hasBatchEditAuth : !hasBatchViewAuth }"
                                        :data-test-id="`process_list_${operate.customAttr}`"
                                        @click="onOperateClick(operate.type)">
                                        {{ operate.value }}
                                    </li>
                                </template>
                            </ul>
                        </bk-dropdown-menu>
                        <div v-if="selectedTpls.length > 0" class="selected-tpl-num">
                            {{ $t('已选择') }}{{ selectedTpls.length }}{{ $t('项') }}
                            <bk-link theme="primary" @click="selectedTpls = []">{{ $t('清空') }}</bk-link>
                        </div>
                    </template>
                </advance-search-form>
                <div class="template-table-content" data-test-id="process_table_processList">
                    <bk-table
                        ref="templateTable"
                        class="template-table"
                        :data="templateList"
                        :pagination="pagination"
                        :size="setting.size"
                        :default-sort="getDefaultSortConfig"
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
                            :prop="item.key || item.id"
                            :width="item.width"
                            :min-width="item.min_width"
                            :render-header="renderTableHeader"
                            :sort-orders="['descending', 'ascending', null]"
                            :sortable="sortableCols.find(col => col.value === (item.key || item.id)) ? 'custom' : false">
                            <template slot-scope="{ row }">
                                <!--流程名称-->
                                <div v-if="item.id === 'name'">
                                    <a
                                        data-test-id="process_table_collectBtn"
                                        v-cursor="{ active: !hasPermission(['flow_view'], row.auth_actions) }"
                                        href="javascript:void(0);"
                                        class="common-icon-favorite icon-favorite"
                                        :class="{
                                            'is-active': row.is_collected,
                                            'disable': collectingId === row.id,
                                            'text-permission-disable': !hasPermission(['flow_view'], row.auth_actions)
                                        }"
                                        @click="onCollectTemplate(row)">
                                    </a>
                                    <template>
                                        <a
                                            v-if="!hasPermission(['flow_view'], row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            @click="onTemplatePermissionCheck(['flow_view'], row)">
                                            {{row.name}}
                                        </a>
                                        <router-link
                                            v-else
                                            class="template-name"
                                            :title="row.name"
                                            :to="getJumpUrl('view', row.id)">
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
                                            data-test-id="process_table_newTaskBtn"
                                            @click="onTemplatePermissionCheck(['flow_create_task'], props.row)">
                                            {{$t('新建任务')}}
                                        </a>
                                        <router-link
                                            v-else
                                            class="template-operate-btn"
                                            data-test-id="process_table_newTaskBtn"
                                            :to="getJumpUrl('newTask', props.row.id)">
                                            {{$t('新建任务')}}
                                        </router-link>
                                        <a
                                            v-if="!hasPermission(['flow_view'], props.row.auth_actions)"
                                            v-cursor
                                            class="text-permission-disable"
                                            data-test-id="process_table_cloneBtn"
                                            @click="onTemplatePermissionCheck(['flow_view'], props.row)">
                                            {{$t('克隆')}}
                                        </a>
                                        <router-link
                                            v-else
                                            class="template-operate-btn"
                                            data-test-id="process_table_cloneBtn"
                                            :to="getJumpUrl('clone', props.row.id)">
                                            {{$t('克隆')}}
                                        </router-link>
                                        <router-link
                                            class="template-operate-btn"
                                            data-test-id="process_table_executeHistoryBtn"
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
                                            :tippy-options="{ boundary: 'window', duration: [0, 0], hideOnClick: false }"
                                            :on-show="onShowMoreOperation">
                                            <i class="bk-icon icon-more drop-icon-ellipsis"></i>
                                            <ul slot="content">
                                                <li class="opt-btn" data-test-id="process_table_editBtn">
                                                    <a
                                                        v-if="!hasPermission(['flow_edit'], props.row.auth_actions)"
                                                        v-cursor
                                                        class="text-permission-disable"
                                                        @click="onTemplatePermissionCheck(['flow_edit'], props.row)">
                                                        {{$t('编辑')}}
                                                    </a>
                                                    <router-link
                                                        v-else
                                                        tag="a"
                                                        :to="getJumpUrl('edit', props.row.id)">
                                                        {{$t('编辑')}}
                                                    </router-link>
                                                </li>
                                                <li class="opt-btn" data-test-id="process_table_deleteBtn">
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
                            <table-setting-content
                                :fields="setting.fieldList"
                                :selected="setting.selectedFields"
                                :size="setting.size"
                                :sortable-cols="sortableCols"
                                :order="ordering"
                                @setting-change="handleSettingChange">
                            </table-setting-content>
                        </bk-table-column>
                        <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
                    </bk-table>
                </div>
            </div>
        </skeleton>
        <ImportDatTplDialog
            :auth-actions="authActions"
            :is-import-dialog-show="isImportDialogShow"
            @onImportConfirm="onImportConfirm"
            @onImportCancel="onImportCancel">
        </ImportDatTplDialog>
        <ImportYamlTplDialog
            :auth-actions="authActions"
            :project_id="project_id"
            :project-name="projectName"
            :is-show.sync="isImportYamlDialogShow"
            @confirm="onImportYamlSuccess">
        </ImportYamlTplDialog>
        <ExportTemplateDialog
            :is-export-dialog-show.sync="isExportDialogShow"
            :selected="selectedTpls"
            :project_id="project_id"
            :type="exportType">
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
    import ImportDatTplDialog from './ImportDatTplDialog.vue'
    import ImportYamlTplDialog from './ImportYamlTplDialog.vue'
    import ExportTemplateDialog from './ExportTemplateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import TableSettingContent from '@/components/common/TableSettingContent.vue'
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
            key: 'pipeline_template__create_time',
            id: 'create_time',
            label: i18n.t('创建时间'),
            width: 200
        },
        {
            key: 'pipeline_template__edit_time',
            id: 'edit_time',
            label: i18n.t('更新时间'),
            width: 200
        },
        {
            id: 'subprocess_has_update',
            label: i18n.t('子流程更新'),
            width: 180
        },
        {
            key: 'category',
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
            ListPageTipsTitle,
            AdvanceSearchForm,
            TableSettingContent,
            NoData
        },
        mixins: [permission],
        props: {
            project_id: [String, Number]
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
            const isSearchFormOpen = SEARCH_FORM.some(item => this.$route.query[item.key])
            // 获取操作列表
            const noViewAuthTip = i18n.t('已选流程模板没有查看权限，请取消选择或申请权限')
            const noEditAuthTip = i18n.t('已选流程模板没有编辑权限，请取消选择或申请权限')
            const operateList = [
                {
                    type: 'dat',
                    content: noViewAuthTip,
                    value: i18n.t('导出为') + 'DAT',
                    customAttr: 'exportDatFile'
                }, {
                    type: 'yaml',
                    content: noViewAuthTip,
                    value: i18n.t('导出为') + 'YAML',
                    customAttr: 'exportYamlFile'
                }, {
                    type: 'collect',
                    content: noViewAuthTip,
                    value: i18n.t('收藏'),
                    customAttr: 'collectProcess'
                }, {
                    type: 'cancelCollect',
                    content: noViewAuthTip,
                    value: i18n.t('取消收藏'),
                    customAttr: 'cancelCollect'
                }, {
                    type: 'delete',
                    content: noEditAuthTip,
                    value: i18n.t('删除'),
                    isOther: true,
                    customAttr: 'deleteProcess'
                }
            ]
            return {
                firstLoading: true,
                listLoading: false,
                projectInfoLoading: true, // 模板分类信息 loading
                configLoading: true,
                searchStr: '',
                searchForm,
                isSearchFormOpen, // 高级搜索表单默认展开
                exportType: 'dat', // 模板导出类型
                operateList,
                expiredSubflowTplList: [],
                selectedTpls: [], // 选中的流程模板
                templateList: [],
                sortableCols: [],
                isDeleteDialogShow: false,
                isImportDialogShow: false,
                isImportYamlDialogShow: false,
                isExportDialogShow: false,
                isAuthorityDialogShow: false,
                theDeleteTemplateId: undefined,
                theAuthorityManageId: undefined,
                active: true,
                pending: {
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
                isInit: true, // 避免default-sort在初始化时去触发table的sort-change事件
                totalPage: 1,
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                collectingId: '', // 正在被收藏/取消收藏的模板id
                ordering: this.$store.state.project.config.task_template_ordering, // 排序参数
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
                'v1_import_flag': state => state.v1_import_flag,
                'username': state => state.username
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'authActions': state => state.authActions,
                'projectName': state => state.projectName
            }),
            crtPageSelectedAll () {
                return this.templateList.length > 0 && this.templateList.every(item => this.selectedTpls.find(tpl => tpl.id === item.id))
            },
            hasBatchViewAuth () {
                let result = false
                if (this.selectedTpls.length) {
                    result = this.selectedTpls.every(template => this.hasPermission(['flow_view'], template.auth_actions))
                }
                return result
            },
            hasBatchEditAuth () {
                let result = false
                if (this.selectedTpls.length) {
                    result = this.selectedTpls.every(template => this.hasPermission(['flow_delete'], template.auth_actions))
                }
                return result
            },
            // 获取默认排序配置
            getDefaultSortConfig () {
                const { ordering } = this
                if (ordering) {
                    if (/^-/.test(this.ordering)) {
                        return { prop: ordering.replace(/^-/, ''), order: 'descending' }
                    }
                    return { prop: ordering, order: 'ascending' }
                }
                return {}
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
            this.getProjectBaseInfo()
            this.getProjectLabelList()
            this.getExpiredSubflowData()
            this.onSearchInput = tools.debounce(this.searchInputHandler, 500)
            await this.initData()
            this.firstLoading = false
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
                'addToCollectList',
                'deleteCollect'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList',
                'batchCancelCollectTpl',
                'deleteTemplate',
                'templateImport',
                'getExpiredSubProcess',
                'batchDeleteTpl'
            ]),
            ...mapActions('project/', [
                'getProjectLabelsWithDefault',
                'getUserProjectConfigOptions',
                'setUserProjectConfig'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async initData () {
                try {
                    this.configLoading = true
                    const res = await this.getUserProjectConfigOptions({ id: this.project_id, params: { configs: 'task_template_ordering' } })
                    this.sortableCols = res.data.task_template_ordering
                    this.getTemplateList()
                } catch (e) {
                    console.error(e)
                } finally {
                    this.configLoading = false
                }
            },
            async getTemplateList () {
                this.listLoading = true
                try {
                    const data = this.getQueryData()
                    let templateListData = {}
                    templateListData = await this.loadTemplateList(data)
                    this.templateList = templateListData.results
                    this.pagination.count = templateListData.count
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
                    this.isInit = false
                }
            },
            getQueryData () {
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
                    limit: this.pagination.limit,
                    offset: (this.pagination.current - 1) * this.pagination.limit,
                    pipeline_template__name__icontains: flowName || undefined,
                    pipeline_template__creator__contains: creator || undefined,
                    category: category || undefined,
                    label_ids: label_ids && label_ids.length ? label_ids.join(',') : undefined,
                    subprocess_has_update__exact: subprocess_has_update,
                    has_subprocess,
                    project__id: this.project_id,
                    new: true
                }
                const keys = ['edit_time', '-edit_time', 'create_time', '-create_time']
                if (keys.includes(this.ordering)) {
                    const symbol = /^-/.test(this.ordering) ? '-' : ''
                    const orderVal = this.ordering.replace(/^-/, '')
                    data['order_by'] = `${symbol}pipeline_template__${orderVal}`
                } else {
                    data['order_by'] = this.ordering
                }
                if (queryTime[0] && queryTime[1]) {
                    data['pipeline_template__edit_time__gte'] = moment.tz(queryTime[0], this.timeZone).format('YYYY-MM-DD')
                    data['pipeline_template__edit_time__lte'] = moment.tz(queryTime[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                }
                return data
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('templateList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.defaultSelected
                    if (!fieldList || !size) {
                        localStorage.removeItem('templateList')
                    }
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
            searchInputHandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
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
                                        self.onSelectTplAll('current')
                                    }
                                }
                            }, [i18n.t('本页全选')]),
                            h('div', {
                                'class': 'mode-item',
                                on: {
                                    click: function () {
                                        self.onSelectTplAll('full')
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
                    this.onSelectTplAll('current')
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
            async onSelectTplAll (type) {
                if (type === 'full') {
                    const data = this.getQueryData()
                    data.limit = 0
                    data.offset = 0
                    const res = await this.loadTemplateList(data)
                    this.selectedTpls = res.results.slice(0)
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
                if (this.selectedTpls.length === 0 || !this.hasBatchViewAuth) {
                    return
                }
                this.batchCollectPending = true
                try {
                    const data = this.selectedTpls.filter(tpl => !tpl.is_collected).map(tpl => {
                        return {
                            extra_info: {
                                project_id: this.project_id,
                                project_name: tpl.project.name,
                                template_id: tpl.id,
                                name: tpl.name,
                                id: tpl.id
                            },
                            instance_id: tpl.id,
                            username: this.username,
                            category: 'flow'
                        }
                    })
                    if (data.length === 0) { // 所选流程都已是收藏状态
                        this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        return
                    }
                    const res = await this.addToCollectList(data)
                    res.data.forEach(item => {
                        // 修改对应的流程（用于单个取消收藏）
                        const tempInfo = this.templateList.find(val => val.id === item.instance_id)
                        if (tempInfo) {
                            tempInfo.is_collected = 1
                            tempInfo.collection_id = item.id
                        }
                        // 修改对应勾选中的流程（用于批量取消收藏）
                        const selectInfo = this.selectedTpls.find(val => val.id === item.instance_id)
                        if (selectInfo) {
                            selectInfo.is_collected = 1
                            selectInfo.collection_id = item.id
                        }
                    })
                    if (res.data.length) {
                        this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.batchCollectPending = false
                }
            },
            onBatchDelete () {
                if (this.selectedTpls.length === 0 || this.batchDeletePending || !this.hasBatchEditAuth) {
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
                        this.$bkMessage({
                            message: i18n.t('流程') + i18n.t('删除成功！'),
                            theme: 'success'
                        })
                        this.pagination.current = 1
                        this.getTemplateList()
                    } else if (Object.keys(res.data.references).length) {
                        const deleteArr = []
                        Object.values(res.data.references).forEach(item => {
                            const value = item.template[0]
                            deleteArr.push(`${value.name}(${value.id})`)
                        })
                        this.$bkMessage({
                            message: i18n.t('流程') + deleteArr.join(i18n.t('，')) + i18n.t('删除失败！'),
                            theme: 'error'
                        })
                    }
                }
                return Promise.resolve()
            },
            onImportConfirm () {
                this.isImportDialogShow = false
                this.getTemplateList()
            },
            onImportCancel () {
                this.isImportDialogShow = false
            },
            onImportYamlSuccess () {
                this.isImportYamlDialogShow = false
                this.getTemplateList()
            },
            onOperateClick (type) {
                switch (type) {
                    case 'collect':
                        if (!this.hasBatchViewAuth) return
                        this.onBatchCollect()
                        break
                    case 'cancelCollect':
                        if (!this.hasBatchViewAuth) return
                        this.onBatchCancelCollect()
                        break
                    case 'delete':
                        if (!this.hasBatchEditAuth) return
                        this.onBatchDelete()
                        break
                    default:
                        if (!this.hasBatchViewAuth) return
                        this.onExportTemplate(type)
                        break
                }
            },
            onExportTemplate (type) {
                this.exportType = type
                this.isExportDialogShow = true
            },
            onDeleteTemplate (template) {
                if (!this.hasPermission(['flow_delete'], template.auth_actions)) {
                    this.onTemplatePermissionCheck(['flow_delete'], template)
                    return
                }
                this.theDeleteTemplateId = template.id
                this.deleteTemplateName = template.name
                this.isDeleteDialogShow = true
            },
            // 表格功能选项
            handleSettingChange ({ fields, size, order }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('templateList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
                if (order && order !== this.ordering) {
                    this.ordering = order
                    this.$refs.templateTable.clearSort()
                    this.$refs.templateTable.sort(/^-/.test(order) ? order.replace(/^-/, '') : order, /^-/.test(order) ? 'descending' : 'ascending')
                    // this.getTemplateList()
                    this.setUserProjectConfig({ id: this.project_id, params: { task_template_ordering: order } })
                }
            },
            handleSortChange ({ prop, order }) {
                if (this.isInit) return
                if (order === 'ascending') {
                    this.ordering = prop
                } else if (order === 'descending') {
                    this.ordering = '-' + prop
                } else {
                    this.ordering = ''
                }
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
                if (this.ordering) {
                    this.setUserProjectConfig({ id: this.project_id, params: { task_template_ordering: this.ordering } })
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property !== 'category') {
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
                this.$router.replace({ name: this.$route.name, params: { project_id: this.project_id }, query })
            },
            /**
             * 单个模板操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 模板数据对象
             */
            onTemplatePermissionCheck (required, template) {
                const project = {
                    id: this.project_id,
                    name: this.projectName
                }
                const authActions = [...this.authActions, ...template.auth_actions]
                this.applyForPermission(required, authActions, { flow: [template], project: [project] })
            },
            async onDeleteConfirm () {
                if (this.pending.delete) return
                this.pending.delete = true
                try {
                    const data = {
                        templateId: this.theDeleteTemplateId
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
                    'view': { name: 'templatePanel', params: { type: 'view' } },
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
                    this.onTemplatePermissionCheck(['flow_view'], template)
                    return
                }

                if (typeof this.collectingId === 'number') {
                    return
                }

                try {
                    this.collectingId = template.id
                    if (!template.is_collected) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                project_id: template.project.id,
                                project_name: template.project.name,
                                template_id: template.template_id,
                                template_source: template.template_source,
                                name: template.name,
                                id: template.id
                            },
                            instance_id: template.id,
                            username: this.username,
                            category: 'flow'
                        }])
                        if (res.data.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                        template.collection_id = res.data[0].id
                    } else { // cancel
                        await this.deleteCollect(template.collection_id)
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                        template.collection_id = 0
                    }
                    template.is_collected = template.is_collected ? 0 : 1
                } catch (e) {
                    console.log(e)
                } finally {
                    this.collectingId = ''
                }
            },
            // 批量取消收藏
            async onBatchCancelCollect () {
                if (this.selectedTpls.length === 0 || !this.hasBatchViewAuth) {
                    return
                }
                
                try {
                    const cancelList = this.selectedTpls.reduce((acc, cur) => {
                        if (cur.is_collected) {
                            acc.push(cur.collection_id)
                        }
                        return acc
                    }, []) || []
                    if (cancelList.length === 0) { // 所选流程都已是取消收藏状态
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                        return
                    }
                    await this.batchCancelCollectTpl({
                        projectId: Number(this.project_id),
                        cancelList
                    })
                    // 不重新拉取流程列表，只针对匹配的进行处理
                    this.templateList.forEach(item => {
                        if (cancelList.includes(item.collection_id)) {
                            item.collection_id = 0
                            item.is_collected = 0
                        }
                    })
                    this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                } catch (error) {
                    console.warn(error)
                }
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
    display: flex;
    align-items: center;
    margin-left: 10px;
    font-size: 12px;
    line-height: 1;
    /deep/.bk-link-text {
        margin-left: 6px;
        font-size: 12px;
        line-height: 1;
    }
}
.dialog-content {
    padding: 30px;
    word-break: break-all;
}
.template-table-content {
    background: #ffffff;
    .bk-table-row.hover-row {
        .icon-favorite {
            display: block;
        }
    }
    .icon-favorite {
        position: absolute;
        top: 14px;
        left: -9px;
        font-size: 14px;
        color: #c4c6cc;
        display: none;
        &:hover, &.is-active {
            display: block;
            color: #ff9c01;
        }
    }
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
    /deep/.table-header-tips {
        margin-left: 4px;
        font-size: 14px;
        color: #c4c6cc;
        cursor: pointer;
    }
}
</style>
