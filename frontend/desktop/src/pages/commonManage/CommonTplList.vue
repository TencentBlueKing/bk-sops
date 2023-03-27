/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
                <div class="search-wrapper mb20">
                    <div class="operation-wrap">
                        <bk-button
                            v-cursor="{ active: !hasCreateCommonTplPerm }"
                            theme="primary"
                            style="min-width: 120px;"
                            :class="{
                                'btn-permission-disable': !hasCreateCommonTplPerm
                            }"
                            data-test-id="commonProcess_form_creatProcess"
                            @click="checkCreatePermission">
                            {{$t('新建')}}
                        </bk-button>
                        <bk-dropdown-menu style="margin: 0 14px;">
                            <div class="import-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('导入') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="import-option-list" slot="dropdown-content">
                                <li data-test-id="commonProcess_list_importYamlFile" @click="isImportYamlDialogShow = true">{{ $t('导入') }}YAML{{ $t('文件') }}</li>
                                <li data-test-id="commonProcess_list_importDatFile" @click="isImportDialogShow = true">{{ $t('导入') }}DAT{{ $t('文件') }}</li>
                            </ul>
                        </bk-dropdown-menu>
                        <bk-dropdown-menu
                            style="margin-right: 14px;"
                            :trigger="selectedTpls.length ? 'mouseover' : 'click'"
                            :disabled="!selectedTpls.length">
                            <div class="export-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('导出') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="export-option-list" slot="dropdown-content">
                                <li data-test-id="commonProcess_list_exportYamlFile" @click="onExportTemplate('exportYamlFile')">{{ $t('导出为') }}YAML{{ $t('文件') }}</li>
                                <li data-test-id="commonProcess_list_exportDatFile" @click="onExportTemplate('exportDatFile')">{{ $t('导出为') }}DAT{{ $t('文件') }}</li>
                            </ul>
                        </bk-dropdown-menu>
                        <bk-button
                            class="batch-delete"
                            data-test-id="commonProcess_form_deleteProcess"
                            :disabled="!selectedTpls.length"
                            @click="onBatchDelete">
                            {{$t('删除')}}
                        </bk-button>
                    </div>
                    <bk-button
                        class="my-create-btn"
                        data-test-id="commonProcess_form_myCreateProcess"
                        @click="handleMyCreateFilter">
                        {{$t('我创建的')}}
                    </bk-button>
                    <search-select
                        ref="searchSelect"
                        id="commonTplList"
                        :placeholder="$t('ID/流程名称/标签/子流程更新/创建人/更新人')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="template-table-content" data-test-id="commonProcess_table_processList">
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
                            :class-name="item.id.replace(/_/g, '-')"
                            show-overflow-tooltip
                            :render-header="renderTableHeader"
                            :sort-orders="['descending', 'ascending', null]"
                            :sortable="sortableCols.find(col => col.value === (item.key || item.id)) ? 'custom' : false">
                            <template slot-scope="{ row }">
                                <!--流程名称-->
                                <div v-if="item.id === 'name'" class="name-column">
                                    <a
                                        data-test-id="process_table_collectBtn"
                                        v-cursor="{ active: !hasPermission(['common_flow_view'], row.auth_actions) }"
                                        href="javascript:void(0);"
                                        class="common-icon-favorite icon-favorite"
                                        :class="{
                                            'is-active': row.is_collected,
                                            'disable': collectingId === row.id,
                                            'text-permission-disable': !hasPermission(['common_flow_view'], row.auth_actions)
                                        }"
                                        @click="onCollectTemplate(row)">
                                    </a>
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
                                        @click.prevent="getJumpUrl('view', row.id)">
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
                        <bk-table-column :label="$t('操作')" width="190" class="operation-cell" :fixed="templateList.length ? 'right' : false">
                            <template slot-scope="props">
                                <div class="template-operation" :template-name="props.row.name">
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
                                        <!-- <router-link class="template-operate-btn" :to="getExecuteHistoryUrl(props.row.id)">{{ $t('执行历史') }}</router-link> -->
                                        <bk-popover
                                            theme="light"
                                            placement="bottom-start"
                                            ext-cls="common-dropdown-btn-popver"
                                            :z-index="2000"
                                            :distance="0"
                                            :arrow="false"
                                            :tippy-options="{ boundary: 'window', duration: [0, 0], hideOnClick: false }">
                                            <i class="bk-icon icon-more drop-icon-ellipsis"></i>
                                            <ul slot="content">
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
                            <table-setting-content
                                :fields="setting.fieldList"
                                :selected="setting.selectedFields"
                                :size="setting.size"
                                :sortable-cols="sortableCols"
                                :order="ordering"
                                @setting-change="handleSettingChange">
                            </table-setting-content>
                        </bk-table-column>
                        <div class="selected-tpl-num" slot="prepend" v-if="selectedTpls.length > 0">
                            {{ $t('当前已选择 x 条数据', { num: selectedTpls.length }) }}{{ $t('，') }}
                            <bk-link theme="primary" @click="selectedTpls = []">{{ $t('清除选择') }}</bk-link>
                        </div>
                        <div class="empty-data" slot="empty">
                            <NoData
                                :type="searchSelectValue.length ? 'search-empty' : 'empty'"
                                :message="searchSelectValue.length ? $t('搜索结果为空') : ''"
                                @searchClear="searchSelectValue = []">
                            </NoData>
                        </div>
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
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import ImportDatTplDialog from '@/pages/template/TemplateList/ImportDatTplDialog.vue'
    import ImportYamlTplDialog from '@/pages/template/TemplateList/ImportYamlTplDialog.vue'
    import ExportTemplateDialog from '@/pages/template/TemplateList/ExportTemplateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TableSettingContent from '@/components/common/TableSettingContent.vue'
    import permission from '@/mixins/permission.js'
    import SelectProjectModal from '@/components/common/modal/SelectProjectModal.vue'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    import CancelRequest from '@/api/cancelRequest.js'

    const SEARCH_LIST = [
        {
            id: 'template_id',
            name: 'ID'
        },
        {
            id: 'flowName',
            name: i18n.t('流程名'),
            isDefaultOption: true
        },
        {
            id: 'subprocessUpdateVal',
            name: i18n.t('子流程更新'),
            children: [
                { id: 1, name: i18n.t('是') },
                { id: -1, name: i18n.t('否') },
                { id: 0, name: i18n.t('无子流程') }
            ]
        },
        {
            id: 'creator',
            name: i18n.t('创建人')
        },
        {
            id: 'editor',
            name: i18n.t('更新人')
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
            key: 'pipeline_template__create_time',
            id: 'create_time',
            label: i18n.t('创建时间'),
            width: 200
        },
        {
            key: 'pipeline_template__edit_time',
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
            SelectProjectModal,
            NoData,
            TableSettingContent,
            SearchSelect
        },
        mixins: [permission],
        data () {
            const {
                page = 1,
                limit = 15,
                create_time = '',
                edit_time = '',
                subprocessUpdateVal = '',
                creator = '',
                editor = '',
                flowName = '',
                template_id = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'create_time', name: i18n.t('创建时间'), type: 'dateRange' },
                { id: 'edit_time', name: i18n.t('更新时间'), type: 'dateRange' }
            ]
            const searchSelectValue = searchList.reduce((acc, cur) => {
                const values_text = this.$route.query[cur.id]
                if (values_text) {
                    let values = []
                    if (!cur.children) {
                        values = cur.type === 'dateRange' ? values_text.split(',') : [values_text]
                        acc.push({ ...cur, values })
                    } else if (cur.children.length) {
                        const ids = values_text.split(',')
                        values = cur.children.filter(item => ids.includes(String(item.id)))
                        acc.push({ ...cur, values })
                    }
                }
                return acc
            }, [])
            // 获取操作列表
            const noViewAuthTip = i18n.t('已选流程模板没有查看权限，请取消选择或申请权限')
            const noEditAuthTip = i18n.t('已选流程模板没有编辑权限，请取消选择或申请权限')
            const operatList = [
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
                exportType: 'dat', // 模板导出类型
                operatList,
                expiredSubflowTplList: [],
                selectedTpls: [], // 选中的流程模板
                templateList: [],
                sortableCols: [],
                isImportDialogShow: false,
                isImportYamlDialogShow: false,
                isExportDialogShow: false,
                isAuthorityDialogShow: false,
                isSelectProjectShow: false,
                theAuthorityManageId: undefined,
                active: true,
                pending: {
                    export: false, // 导出
                    delete: false // 删除
                },
                templateCategoryList: [],
                editEndTime: undefined,
                templateType: this.common_template,
                requestData: {
                    subprocessUpdateVal: subprocessUpdateVal !== '' ? Number(subprocessUpdateVal) : '',
                    creator,
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    edit_time: edit_time ? edit_time.split(',') : ['', ''],
                    flowName,
                    template_id,
                    editor
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
                ordering: this.$store.state.project.commonConfig.task_template_ordering, // 排序参数
                tableFields: TABLE_FIELDS,
                defaultSelected: ['id', 'name', 'label', 'edit_time', 'subprocess_has_update', 'creator_name'],
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                },
                isInit: true, // 避免default-sort在初始化时去触发table的sort-change事件
                categoryTips: i18n.t('模板分类即将下线，建议使用标签'),
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username,
                'site_url': state => state.site_url,
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
            },
            hasBatchViewAuth () {
                let result = false
                if (this.selectedTpls.length) {
                    result = this.selectedTpls.every(template => this.hasPermission(['common_flow_view'], template.auth_actions))
                }
                return result
            },
            hasBatchEditAuth () {
                let result = false
                if (this.selectedTpls.length) {
                    result = this.selectedTpls.every(template => this.hasPermission(['common_flow_delete'], template.auth_actions))
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
            this.queryCreateCommonTplPerm()
            // 获取表头排序列表和设置
            const res = await this.getUserProjectConfigOptions({ id: -1, params: { configs: 'task_template_ordering' } })
            this.sortableCols = res.data.task_template_ordering
            const commonConfig = await this.getUserProjectConfigs(-1)
            this.setCommonConfig(commonConfig.data)
            this.ordering = commonConfig.data.task_template_ordering

            await this.getTemplateList()
            this.firstLoading = false
        },
        methods: {
            ...mapMutations('project', [
                'setCommonConfig'
            ]),
            ...mapActions([
                'queryUserPermission',
                'addToCollectList',
                'deleteCollect'
            ]),
            ...mapActions('project/', [
                'getUserProjectConfigOptions',
                'getUserProjectConfigs',
                'setUserProjectConfig'
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
                    const source = new CancelRequest()
                    data.cancelToken = source.token
                    const templateListData = await this.loadTemplateList(data)
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
                const { subprocessUpdateVal, creator, create_time, edit_time, flowName, template_id, editor } = this.requestData
                /**
                 * 无子流程 has_subprocess=false
                 * 有子流程，需要更新 has_subprocess=true&subprocess_has_update=true
                 * 有子流程，不需要更新 has_subprocess=true&subprocess_has_update=false
                 * 不做筛选 has_subprocess=undefined
                 */
                const has_subprocess = (subprocessUpdateVal === 1 || subprocessUpdateVal === -1) ? true : (subprocessUpdateVal === 0 ? false : undefined)
                const subprocess_has_update = subprocessUpdateVal === 1 ? true : (subprocessUpdateVal === -1 ? false : undefined)
                const tplIds = template_id?.split('|').map(item => item.trim()).join(',') || undefined
                const data = {
                    limit: this.pagination.limit,
                    offset: (this.pagination.current - 1) * this.pagination.limit,
                    common: '1',
                    pipeline_template__name__icontains: flowName || undefined,
                    pipeline_template__creator: creator || undefined,
                    subprocess_has_update__exact: subprocess_has_update,
                    pipeline_template__has_subprocess: has_subprocess,
                    new: true,
                    id__in: tplIds,
                    pipeline_template__editor: editor || undefined
                }
                const keys = ['edit_time', '-edit_time', 'create_time', '-create_time']
                if (keys.includes(this.ordering)) {
                    const symbol = /^-/.test(this.ordering) ? '-' : ''
                    const orderVal = this.ordering.replace(/^-/, '')
                    data['order_by'] = `${symbol}pipeline_template__${orderVal}`
                } else {
                    data['order_by'] = this.ordering
                }
                if (create_time && create_time[0] && create_time[1]) {
                    data['pipeline_template__create_time__gte'] = moment(create_time[0]).format('YYYY-MM-DD HH:mm:ss')
                    data['pipeline_template__create_time__lte'] = moment(create_time[1]).format('YYYY-MM-DD HH:mm:ss')
                }
                if (edit_time && edit_time[0] && edit_time[1]) {
                    data['pipeline_template__edit_time__gte'] = moment(edit_time[0]).format('YYYY-MM-DD HH:mm:ss')
                    data['pipeline_template__edit_time__lte'] = moment(edit_time[1]).format('YYYY-MM-DD HH:mm:ss')
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
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.defaultSelected
                    if (!fieldList || !size) {
                        localStorage.removeItem('commonTemplateList')
                    }
                } else {
                    selectedFields = this.defaultSelected
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
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
            // 我创建的
            handleMyCreateFilter () {
                const creatorInfo = this.searchSelectValue.find(item => item.id === 'creator')
                let info = {}
                if (creatorInfo) {
                    creatorInfo.values = [this.username]
                    info = creatorInfo
                } else {
                    const form = this.searchList.find(item => item.id === 'creator')
                    info = { ...form, values: [this.username] }
                    this.searchSelectValue.push(info)
                }
                // 添加搜索记录
                const searchDom = this.$refs.searchSelect
                searchDom && searchDom.addSearchRecord(info)
            },
            handleSearchValueChange (data) {
                data = data.reduce((acc, cur) => {
                    if (cur.type === 'dateRange') {
                        acc[cur.id] = cur.values
                    } else if (cur.multiable) {
                        acc[cur.id] = cur.values.map(item => item.id)
                    } else {
                        const value = cur.values[0]
                        acc[cur.id] = cur.children ? value.id : value
                    }
                    return acc
                }, {})
                this.requestData = data
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
                    this.selectedTpls = res.slice(0)
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
                                template_id: tpl.id,
                                name: tpl.name,
                                id: tpl.id
                            },
                            instance_id: tpl.id,
                            username: this.username,
                            category: 'common_flow'
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
                    title: `${i18n.t('确认删除所选的')} ${this.selectedTpls.length} ${i18n.t('项流程吗') + '?'}`,
                    subTitle: i18n.t('若流程已被其它流程、周期计划任务、轻应用使用，则无法删除'),
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    confirmFn: async () => {
                        await this.batchDeleteConfirm()
                    }
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
                    const { success, fail } = res.data
                    if (fail.length) {
                        const h = this.$createElement
                        const self = this
                        this.$bkMessage({
                            message: h('p', {
                                style: {
                                    margin: 0
                                }
                            }, [
                                i18n.t('x 项删除成功,', { num: success.length }),
                                h('span', {
                                    style: {
                                        color: '#3a84ff',
                                        cursor: 'pointer',
                                        margin: '0 5px'
                                    },
                                    on: {
                                        click: function () {
                                            self.filterDeleteErrorTpls(fail.join(','))
                                        }
                                    }
                                }, fail.length),
                                i18n.t('项删除失败')
                            ]),
                            theme: 'error',
                            delay: 10000
                        })
                    } else {
                        this.$bkMessage({
                            message: i18n.t('流程') + i18n.t('删除成功！'),
                            theme: 'success'
                        })
                    }
                    if (success.length) {
                        success.forEach(id => {
                            const index = this.selectedTpls.findIndex(tpl => tpl.id === id)
                            this.selectedTpls.splice(index, 1)
                        })
                        this.pagination.current = 1
                        this.getTemplateList()
                    }
                }
                return Promise.resolve()
            },
            filterDeleteErrorTpls (templateIds) {
                const creatorInfo = this.searchSelectValue.find(item => item.id === 'template_id')
                if (creatorInfo) {
                    creatorInfo.values = templateIds
                } else {
                    const form = this.searchList.find(item => item.id === 'template_id')
                    this.searchSelectValue.push({ ...form, values: [templateIds] })
                }
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
                if (!this.hasBatchViewAuth) return
                this.exportType = type
                this.isExportDialogShow = true
            },
            onDeleteTemplate (template) {
                if (!this.hasPermission(['common_flow_delete'], template.auth_actions)) {
                    this.onTemplatePermissonCheck(['common_flow_delete'], template)
                    return
                }
                this.$bkInfo({
                    title: i18n.t('确认删除') + i18n.t('流程') + '"' + template.name + '"' + '?',
                    subTitle: i18n.t('若流程已被其它流程、周期计划任务、轻应用使用，则无法删除'),
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    confirmFn: async () => {
                        await this.onDeleteConfirm(template.id)
                    }
                })
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
                // 更新表格头（自定义排序后不会清空其他排序的状态）
                if (prop === 'pipeline_template__create_time') {
                    const tableDom = this.$refs.templateTable
                    const columns = tableDom ? tableDom.store.states.columns : []
                    columns.forEach(column => {
                        if (column.sortable && column.property !== prop) {
                            column.order = null
                        }
                    })
                }
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
                if (this.ordering) {
                    this.setUserProjectConfig({ id: -1, params: { task_template_ordering: this.ordering } })
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property === 'category') {
                    return h('span', {
                        'class': 'category-label'
                    }, [
                        h('p', {
                            'class': 'label-text',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [column.label]),
                        h('i', {
                            'class': 'common-icon-info table-header-tips',
                            directives: [{
                                name: 'bk-tooltips',
                                value: this.categoryTips
                            }]
                        })
                    ])
                } else if (['pipeline_template__create_time', 'pipeline_template__edit_time'].includes(column.property)) {
                    const id = this.setting.selectedFields[$index - 1].id
                    const date = this.requestData[id]
                    return <TableRenderHeader
                        name={ column.label }
                        property={ column.property }
                        sortConfig={ this.getDefaultSortConfig }
                        dateValue={ date }
                        onSortChange={ data => this.handleSortChange(data) }
                        onDateChange={ data => this.handleDateTimeFilter(data, id) }>
                    </TableRenderHeader>
                } else {
                    return h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        column.label
                    ])
                }
            },
            handleDateTimeFilter (date = [], id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                if (date.length) {
                    if (index > -1) {
                        this.searchSelectValue[index].values = date
                    } else {
                        const info = {
                            id,
                            type: 'dateRange',
                            name: id === 'create_time' ? i18n.t('创建时间') : i18n.t('更新时间'),
                            values: date
                        }
                        this.searchSelectValue.push(info)
                        // 添加搜索记录
                        const searchDom = this.$refs.searchSelect
                        searchDom && searchDom.addSearchRecord(info)
                    }
                } else if (index > -1) {
                    this.searchSelectValue.splice(index, 1)
                }
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
            handleSettingChange ({ fields, size, order }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('commonTemplateList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
                if (order && order !== this.ordering) {
                    this.ordering = order
                    this.$refs.templateTable.clearSort()
                    this.$refs.templateTable.sort(/^-/.test(order) ? order.replace(/^-/, '') : order, /^-/.test(order) ? 'descending' : 'ascending')
                    this.setUserProjectConfig({ id: -1, params: { task_template_ordering: order } })
                }
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { create_time, edit_time, subprocessUpdateVal, creator, flowName, template_id, editor } = this.requestData
                const filterObj = {
                    limit,
                    subprocessUpdateVal,
                    creator,
                    page: current,
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    edit_time: edit_time && edit_time.every(item => item) ? edit_time.join(',') : '',
                    flowName,
                    template_id,
                    editor
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.replace({ name: this.$route.name, query })
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
            async onDeleteConfirm (templateId) {
                if (this.pending.delete) return
                this.pending.delete = true
                try {
                    const data = {
                        templateId,
                        common: '1'
                    }
                    const resp = await this.deleteTemplate(data)
                    if (resp.result === false) return
                    if (this.selectedTpls.find(tpl => tpl.id === templateId)) {
                        const index = this.selectedTpls.findIndex(tpl => tpl.id === templateId)
                        this.selectedTpls.splice(index, 1)
                    }
                    // 最后一页最后一条删除后，往前翻一页
                    if (
                        this.pagination.current > 1
                        && this.totalPage === this.pagination.current
                        && this.pagination.count - (this.totalPage - 1) * this.pagination.limit === 1
                    ) {
                        this.pagination.current -= 1
                    }
                    this.getTemplateList()
                    this.$bkMessage({
                        message: i18n.t('公共流程') + i18n.t('删除成功！'),
                        theme: 'success'
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.delete = false
                }
            },
            /**
             * 获取模版操作的跳转链接
             * @param {string} name -类型
             * @param {Number} template_id -模版id(可选)
             */
            getJumpUrl (name, template_id) {
                const urlMap = {
                    'view': { name: 'commonTemplatePanel', params: { type: 'view' } },
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
                    if (!template.is_collected) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                template_id: template.template_id,
                                name: template.name,
                                id: template.id
                            },
                            instance_id: template.id,
                            username: this.username,
                            category: 'common_flow'
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
.search-wrapper {
    position: relative;
    display: flex;
    justify-content: space-between;
    .operation-wrap {
        display: flex;
    }
    .my-create-btn {
        position: absolute;
        right: 495px;
    }
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
    line-height: 30px;
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
    height: 32px !important;
    &:hover {
        .export-tpl-btn,
        .import-tpl-btn {
            border-color: #979ba5;
            .bk-icon {
                transform: rotate(180deg);
            }
        }
    }
    .bk-icon {
        margin-left: 3px;
    }
    &.disabled .export-tpl-btn {
        cursor: not-allowed;
    }
    /deep/.bk-dropdown-content {
        z-index: 1;
    }
}
.export-option-list,
.import-option-list {
    & > li {
        padding: 0 10px;
        height: 32px;
        line-height: 30px;
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
.batch-delete {
    &.is-disabled {
        border-color: #dcdee5 !important;
        background-color: #fafafa !important;
    }
}
.selected-tpl-num {
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    background: #f0f1f5;
    border-bottom: 1px solid #dfe0e5;
    /deep/.bk-link-text {
        margin-left: 6px;
        font-size: 12px;
        line-height: 1;
    }
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
        &.is-active {
            display: block;
            color: #ff9c01;
        }
    }
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
    /deep/.category-label {
        display: flex;
        align-items: center;
        .table-header-tips {
            flex-shrink: 0;
            margin-left: 4px;
            font-size: 14px;
            color: #c4c6cc;
            cursor: pointer;
        }
    }
    /deep/.edit-time,
    /deep/.create-time {
        .bk-table-caret-wrapper {
            display: none;
        }
    }
}
</style>
