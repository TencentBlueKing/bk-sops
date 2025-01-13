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
                <list-page-tips-title
                    :num="expiredSubflowTplList.length"
                    @viewClick="handleSubflowFilter">
                </list-page-tips-title>
                <div class="search-wrapper mb20">
                    <div class="operation-wrap">
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
                        <bk-dropdown-menu>
                            <div class="import-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('导入') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="import-option-list" slot="dropdown-content">
                                <li data-test-id="process_list_importYamlFile" @click="isImportYamlDialogShow = true">{{ $t('导入') }} YAML {{ $t('文件') }}</li>
                                <li data-test-id="process_list_importDatFile" @click="isImportDialogShow = true">{{ $t('导入') }} DAT {{ $t('文件') }}</li>
                            </ul>
                        </bk-dropdown-menu>
                        <bk-dropdown-menu
                            :trigger="selectedTpls.length ? 'mouseover' : 'click'"
                            :disabled="!selectedTpls.length">
                            <div class="export-tpl-btn" slot="dropdown-trigger">
                                <span>{{ $t('导出') }}</span>
                                <i :class="['bk-icon icon-angle-down']"></i>
                            </div>
                            <ul class="export-option-list" slot="dropdown-content">
                                <li data-test-id="process_list_exportYamlFile" @click="onExportTemplate('exportYamlFile')">{{ $t('导出为') }} YAML {{ $t('文件') }}</li>
                                <li data-test-id="process_list_exportDatFile" @click="onExportTemplate('exportDatFile')">{{ $t('导出为') }} DAT {{ $t('文件') }}</li>
                            </ul>
                        </bk-dropdown-menu>
                        <SharedTemplateBtn
                            v-if="isEnableTemplateMarket"
                            :project_id="project_id"
                            :selected="selectedTpls">
                        </SharedTemplateBtn>
                        <bk-button
                            class="batch-delete"
                            data-test-id="process_form_deleteProcess"
                            :disabled="!selectedTpls.length"
                            @click="onBatchDelete">
                            {{$t('删除')}}
                        </bk-button>
                    </div>
                    <bk-button
                        class="my-create-btn"
                        data-test-id="process_form_myCreateProcess"
                        @click="handleMyCreateFilter">
                        {{$t('我创建的')}}
                    </bk-button>
                    <search-select
                        ref="searchSelect"
                        id="templateList"
                        :placeholder="$t('ID/流程名称/标签/更新人/创建人/子流程更新/执行代理人')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
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
                            :class-name="item.id.replace(/_/g, '-')"
                            show-overflow-tooltip
                            :render-header="renderTableHeader"
                            :sort-orders="['descending', 'ascending', null]"
                            :sortable="sortableCols.find(col => col.value === (item.key || item.id)) ? 'custom' : false">
                            <template slot-scope="{ row }">
                                <!--流程名称-->
                                <div v-if="item.id === 'name'" class="flow-name-column">
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
                                <template v-else-if="item.id === 'label'">
                                    <div
                                        v-if="row.isSelectShow"
                                        class="label-select"
                                        v-bkloading="{ isLoading: row.labelLoading }"
                                        v-bk-clickoutside="handleClickOutSide">
                                        <bk-select
                                            :key="templateLabels.length"
                                            ref="labelSelect"
                                            v-model="row.labelIds"
                                            ext-popover-cls="label-select-popover"
                                            :display-tag="true"
                                            :multiple="true"
                                            searchable
                                            :popover-options="{
                                                onHide: () => !labelDialogShow
                                            }"
                                            ext-cls="label-select"
                                            @toggle="onToggleTplLabel">
                                            <div class="label-select-content" v-bkloading="{ isLoading: templateLabelLoading }">
                                                <bk-option
                                                    v-for="(label, index) in templateLabels"
                                                    :key="index"
                                                    :id="label.id"
                                                    :name="label.name">
                                                    <div class="label-select-option">
                                                        <span
                                                            class="label-select-color"
                                                            :style="{ background: label.color }">
                                                        </span>
                                                        <span>{{label.name}}</span>
                                                        <i v-if="row.labelIds.includes(label.id)" class="bk-option-icon bk-icon icon-check-1"></i>
                                                    </div>
                                                </bk-option>
                                            </div>
                                            <div slot="extension" class="label-select-extension">
                                                <div
                                                    class="add-label"
                                                    data-test-id="process_list__editLabel"
                                                    v-cursor="{ active: !hasPermission(['project_edit'], authActions) }"
                                                    @click="onEditLabel">
                                                    <i class="bk-icon icon-plus-circle"></i>
                                                    <span>{{ $t('新建标签') }}</span>
                                                </div>
                                                <div
                                                    class="label-manage"
                                                    data-test-id="process_list__labelManage"
                                                    v-cursor="{ active: !hasPermission(['project_view'], authActions) }"
                                                    @click="onManageLabel">
                                                    <i class="common-icon-label"></i>
                                                    <span>{{ $t('标签管理') }}</span>
                                                </div>
                                                <div
                                                    class="refresh-label"
                                                    data-test-id="process_list__refreshLabel"
                                                    @click="getProjectLabelList">
                                                    <i class="bk-icon icon-right-turn-line"></i>
                                                </div>
                                            </div>
                                        </bk-select>
                                    </div>
                                    <div
                                        v-else
                                        class="label-column"
                                        v-cursor="{ active: !hasPermission(['flow_edit'], row.auth_actions) }"
                                        @click="handleTempLabelClick(row)">
                                        <template v-if="row.template_labels && row.template_labels.length > 0">
                                            <span
                                                v-for="label in row.template_labels"
                                                class="label-name"
                                                :key="label.id"
                                                :style="{ background: label.color, color: darkColorList.includes(label.color) ? '#fff' : '#262e4f' }">
                                                {{ label.name }}
                                            </span>
                                        </template>
                                        <span v-else>--</span>
                                    </div>
                                </template>
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
                        <bk-table-column :label="$t('操作')" width="240" class="operation-cell" :fixed="templateList.length ? 'right' : false">
                            <template slot-scope="props">
                                <div class="template-operation" :template-name="props.row.name">
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
                                            v-if="!hasPermission(['flow_view', 'flow_create'], [...props.row.auth_actions, ...authActions])"
                                            v-cursor
                                            class="text-permission-disable"
                                            data-test-id="process_table_cloneBtn"
                                            @click="onFlowClone(props.row)">
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
            width="480"
            ext-cls="common-dialog label-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('新建标签')"
            :loading="labelLoading"
            :value="labelDialogShow"
            :cancel-text="$t('取消')"
            @confirm="editLabelConfirm"
            @cancel="labelDialogShow = false">
            <bk-form ref="labelForm" :model="labelDetail" :rules="labelRules">
                <bk-form-item property="name" :label="$t('标签名称')" :required="true">
                    <bk-input v-model="labelDetail.name"></bk-input>
                </bk-form-item>
                <bk-form-item property="color" :label="$t('标签颜色')" :required="true">
                    <bk-dropdown-menu
                        ref="dropdown"
                        trigger="click"
                        class="color-dropdown"
                        @show="colorDropdownShow = true"
                        @hide="colorDropdownShow = false">
                        <div class="dropdown-trigger-btn" slot="dropdown-trigger">
                            <span class="color-block" :style="{ background: labelDetail.color }"></span>
                            <i :class="['bk-icon icon-angle-down',{ 'icon-flip': colorDropdownShow }]"></i>
                        </div>
                        <div class="color-list" slot="dropdown-content">
                            <div class="tip">{{ $t('选择颜色') }}</div>
                            <div>
                                <span
                                    v-for="color in colorList"
                                    :key="color"
                                    class="color-item color-block"
                                    :style="{ background: color }"
                                    @click="labelDetail.color = color">
                                </span>
                            </div>
                        </div>
                    </bk-dropdown-menu>
                </bk-form-item>
                <bk-form-item :label="$t('标签描述')">
                    <bk-input type="textarea" v-model="labelDetail.description"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { DARK_COLOR_LIST, LABEL_COLOR_LIST } from '@/constants/index.js'
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import ImportDatTplDialog from './ImportDatTplDialog.vue'
    import ImportYamlTplDialog from './ImportYamlTplDialog.vue'
    import ExportTemplateDialog from './ExportTemplateDialog.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    import TableSettingContent from '@/components/common/TableSettingContent.vue'
    import SharedTemplateBtn from './SharedTemplate/index.vue'
    // moment用于时区使用
    import moment from 'moment-timezone'
    import ListPageTipsTitle from '../ListPageTipsTitle.vue'
    import CancelRequest from '@/api/cancelRequest.js'

    const categoryTips = i18n.t('模板分类即将下线，建议使用标签')

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
            id: 'label_ids',
            name: i18n.t('标签'),
            children: [],
            multiable: true
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
        },
        {
            id: 'executor_proxy',
            name: i18n.t('执行代理人')
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
            id: 'executor_proxy',
            label: i18n.t('执行代理人'),
            width: 120
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
            SharedTemplateBtn,
            ListPageTipsTitle,
            SearchSelect,
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
                create_time = '',
                edit_time = '',
                subprocessUpdateVal = '',
                creator = '',
                editor = '',
                flowName = '',
                label_ids = '',
                template_id = '',
                executor_proxy = ''
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
                exportType: 'dat', // 模板导出类型
                operateList,
                expiredSubflowTplList: [],
                selectedTpls: [], // 选中的流程模板
                templateList: [],
                sortableCols: [],
                isImportDialogShow: false,
                isImportYamlDialogShow: false,
                isExportDialogShow: false,
                isAuthorityDialogShow: false,
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
                    creator,
                    editor,
                    subprocessUpdateVal: subprocessUpdateVal !== '' ? Number(subprocessUpdateVal) : '',
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    edit_time: edit_time ? edit_time.split(',') : ['', ''],
                    label_ids: label_ids ? label_ids.split(',') : [],
                    flowName,
                    template_id,
                    executor_proxy
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
                categoryTips,
                templateLabels: [],
                labelDialogShow: false,
                labelRules: {
                    color: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }
                    ],
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('标签名称不能超过') + 50 + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return this.templateLabels.every(label => label.name !== val)
                            },
                            message: i18n.t('标签已存在，请重新输入'),
                            trigger: 'blur'
                        }
                    ]
                },
                labelDetail: {},
                colorDropdownShow: false,
                colorList: LABEL_COLOR_LIST,
                labelLoading: false,
                curSelectedRow: {},
                searchList: tools.deepClone(SEARCH_LIST),
                searchSelectValue,
                templateLabelLoading: false,
                isEnableTemplateMarket: window.ENABLE_TEMPLATE_MARKET
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
            this.getProjectLabelList()
            this.getExpiredSubflowData()
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
                'loadProjectBaseInfo',
                'saveTemplateData'
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
                'setUserProjectConfig',
                'createTemplateLabel'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo',
                'setTemplateData'
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
                    const source = new CancelRequest()
                    data.cancelToken = source.token
                    let templateListData = {}
                    templateListData = await this.loadTemplateList(data)
                    this.templateList = templateListData.results.map(item => {
                        item.isSelectShow = false
                        item.labelLoading = false
                        if (item.template_labels && item.template_labels.length > 0) {
                            item.labelIds = item.template_labels.map(label => label.label_id)
                        } else {
                            item.labelIds = []
                        }
                        return item
                    })
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
                const { subprocessUpdateVal, creator, create_time, edit_time, flowName, label_ids, template_id, editor, executor_proxy } = this.requestData

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
                    pipeline_template__name__icontains: flowName || undefined,
                    pipeline_template__creator: creator || undefined,
                    label_ids: label_ids && label_ids.length ? label_ids.join('|') : undefined,
                    subprocess_has_update__exact: subprocess_has_update,
                    pipeline_template__has_subprocess: has_subprocess,
                    project__id: this.project_id,
                    new: true,
                    id__in: tplIds,
                    pipeline_template__editor: editor || undefined,
                    executor_proxy
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
                    data['pipeline_template__create_time__gte'] = moment.tz(create_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    data['pipeline_template__create_time__lte'] = moment.tz(create_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                }
                if (edit_time && edit_time[0] && edit_time[1]) {
                    data['pipeline_template__edit_time__gte'] = moment.tz(edit_time[0], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
                    data['pipeline_template__edit_time__lte'] = moment.tz(edit_time[1], this.timeZone).format('YYYY-MM-DD HH:mm:ss')
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
                const form = this.searchList.find(item => item.id === 'label_ids')
                try {
                    this.templateLabelLoading = true
                    const res = await this.getProjectLabelsWithDefault(this.project_id)
                    this.templateLabels = res.data
                    
                    form.children = res.data.map(item => Object.assign({}, item, { value: item.id }))
                    // 因为标签列表是通过接口获取的，所以需要把路径上的标签添加进去
                    const ids = this.$route.query['label_ids']
                    if (ids) {
                        const values = form.children.filter(item => ids.split(',').includes(String(item.id)))
                        this.searchSelectValue.push({ ...form, values })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLabelLoading = false
                }
            },
            onToggleTplLabel (val) {
                if (val) {
                    window.reportInfo({
                        page: 'templateEdit',
                        zone: 'selectLabel',
                        event: 'click'
                    })
                }
            },
            handleTempLabelClick (row) {
                if (!this.hasPermission(['flow_edit'], row.auth_actions)) {
                    this.onTemplatePermissionCheck(['flow_edit'], row)
                    return
                }
                this.curSelectedRow = tools.deepClone(row)
                row.labelLoading = true
                row.isSelectShow = true
                setTimeout(() => {
                    this.$refs.labelSelect[0].show()
                    row.labelLoading = false
                }, 500)
            },
            handleClickOutSide (e) {
                if (dom.parentClsContains('label-select-popover', e.target)
                    || dom.parentClsContains('label-dialog', e.target)
                    || dom.parentClsContains('permission-dialog', e.target)
                ) {
                    return
                }
                this.saveTemplateLabels()
            },
            async saveTemplateLabels () {
                const curRow = this.templateList.find(item => item.id === this.curSelectedRow.id)
                const match = tools.isDataEqual(curRow.labelIds, this.curSelectedRow.labelIds)
                if (match) {
                    curRow.isSelectShow = false
                    return
                }
                curRow.labelLoading = true
                try {
                    const { id, labelIds: template_labels } = curRow
                    this.setTemplateData({ ...curRow, template_labels })
                    const resp = await this.saveTemplateData({
                        templateId: id,
                        projectId: this.project_id,
                        common: false
                    })
                    if (!resp.result) {
                        if ('errorId' in resp) {
                            this.$bkMessage({
                                message: resp.message,
                                theme: 'error',
                                delay: 10000
                            })
                        }
                        return
                    }
                    // 前端修改对应模板的labels
                    curRow.template_labels = this.templateLabels.reduce((acc, cur) => {
                        const { id, name, color } = cur
                        if (curRow.labelIds.includes(id)) {
                            acc.push({ id, name, color })
                        }
                        return acc
                    }, [])
                    curRow.labelLoading = false
                    this.$nextTick(() => {
                        curRow.isSelectShow = false
                    })
                    this.$bkMessage({
                        message: i18n.t('流程标签修改成功'),
                        theme: 'success'
                    })
                } catch (error) {
                    curRow.labelLoading = false
                    console.warn(error)
                }
            },
            onEditLabel () {
                if (!this.hasPermission(['project_edit'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_edit'], this.authActions, resourceData)
                    return
                }
                this.labelDetail = { color: '#1c9574', name: '', description: '' }
                this.labelDialogShow = true
            },
            onManageLabel () {
                if (!this.hasPermission(['project_view'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_view'], this.authActions, resourceData)
                    return
                }
                const { href } = this.$router.resolve({
                    name: 'projectConfig',
                    params: { id: this.project_id },
                    query: { configActive: 'label_config' }
                })
                window.open(href, '_blank')
            },
            editLabelConfirm () {
                if (this.labelLoading) {
                    return
                }
                this.labelLoading = true
                try {
                    this.$refs.labelForm.validate().then(async result => {
                        if (result) {
                            const { project_id } = this.$route.params
                            const data = {
                                creator: this.username,
                                project_id: Number(project_id),
                                ...this.labelDetail
                            }
                            const resp = await this.createTemplateLabel(data)
                            if (resp.result) {
                                this.labelDialogShow = false
                                this.$bkMessage({
                                    message: i18n.t('标签新建成功'),
                                    theme: 'success'
                                })
                                // 新建标签后自动选上
                                const curRow = this.templateList.find(item => item.id === this.curSelectedRow.id)
                                curRow.labelIds.push(resp.data.id)
                                this.getProjectLabelList()
                            }
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.labelLoading = false
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
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.batchDeleteConfirm()
                    }
                })
            },
            async batchDeleteConfirm () {
                const data = {
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
            onExportTemplate (type) {
                if (!this.hasBatchViewAuth) return
                this.exportType = type
                this.isExportDialogShow = true
            },
            onDeleteTemplate (template) {
                if (!this.hasPermission(['flow_delete'], template.auth_actions)) {
                    this.onTemplatePermissionCheck(['flow_delete'], template)
                    return
                }
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除') + i18n.t('流程') + '"' + template.name + '"' + '?']),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('若流程已被其它流程、周期计划任务、轻应用使用，则无法删除')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.onDeleteConfirm(template.id)
                    }
                })
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
                    this.setUserProjectConfig({ id: this.project_id, params: { task_template_ordering: this.ordering } })
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property === 'category') {
                    return h('p', {
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
                        ref="TableRenderHeader"
                        name={ column.label }
                        property={ column.property }
                        sortConfig={ this.getDefaultSortConfig }
                        dateValue={ date }
                        onSortChange={ data => this.handleSortChange(data) }
                        onDateChange={ data => this.handleDateTimeFilter(data, id) }>
                    </TableRenderHeader>
                } else if (column.property === 'label') {
                    const list = this.templateLabels.map(label => {
                        label.textColor = this.darkColorList.includes(label.color) ? '#fff' : '#262e4f'
                        return label
                    })
                    const data = this.searchSelectValue.find(item => item.id === 'label_ids')
                    const filterConfig = {
                        show: true,
                        list,
                        values: data ? data.values : [],
                        multiple: true
                    }
                    return <TableRenderHeader
                        name={ column.label }
                        property={ column.property }
                        orderShow={ false }
                        dateFilterShow={ false }
                        filterConfig = { filterConfig }
                        onFilterChange={ data => this.handleLabelFilter(data) }>
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
            handleLabelFilter (data = []) {
                const index = this.searchSelectValue.findIndex(item => item.id === 'label_ids')
                if (data.length) {
                    if (index > -1) {
                        const values = this.searchSelectValue[index].values
                        this.searchSelectValue[index].values = [...new Set(values, data)]
                    } else {
                        const form = this.searchList.find(item => item.id === 'label_ids')
                        this.searchSelectValue.push({ ...form, values: data })
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
            updateUrl () {
                const { current, limit } = this.pagination
                const { category, create_time, edit_time, subprocessUpdateVal, creator, label_ids, flowName, template_id, editor, executor_proxy } = this.requestData
                const filterObj = {
                    limit,
                    category,
                    subprocessUpdateVal,
                    creator,
                    page: current,
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    edit_time: edit_time && edit_time.every(item => item) ? edit_time.join(',') : '',
                    label_ids: label_ids && label_ids.length ? label_ids.join(',') : '',
                    flowName: flowName,
                    template_id,
                    editor,
                    executor_proxy
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
            async onDeleteConfirm (templateId) {
                if (this.pending.delete) return
                this.pending.delete = true
                try {
                    const data = { templateId }
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
                        message: i18n.t('流程') + i18n.t('删除成功！'),
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
                const subFlowInfo = this.searchSelectValue.find(item => item.id === 'subprocessUpdateVal')
                if (subFlowInfo) {
                    subFlowInfo.values = [{ id: 1, name: i18n.t('是') }]
                } else {
                    const form = this.searchList.find(item => item.id === 'subprocessUpdateVal')
                    this.searchSelectValue.push({ ...form, values: [{ id: 1, name: i18n.t('是') }] })
                }
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
            },
            onFlowClone (row) {
                const applyAuth = []
                if (!this.hasPermission(['flow_view'], row.auth_actions)) {
                    applyAuth.push('flow_view')
                }
                if (!this.hasPermission(['flow_create'], this.authActions)) {
                    applyAuth.unshift('flow_create')
                }
                this.onTemplatePermissionCheck(applyAuth, row)
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
        align-items: center;
        > * {
            margin-right: 14px;
        }
    }
    .my-create-btn {
        position: absolute;
        right: 495px;
    }
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
    line-height: 30px;
    min-width: 88px;
    text-align: center;
    font-size: 14px;
    color: #63656e;
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
.import-option-list,
.export-option-list {
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
.batch-delete {
    &.is-disabled {
        border-color: #dcdee5 !important;
        background-color: #fafafa !important;
    }
}
/deep/.bk-table-header-append .is-prepend {
    height: 32px !important;
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
    /deep/.bk-table {
        td, th {
            height: 42px;
        }
    }
    .icon-favorite {
        position: absolute;
        left: -9px;
        font-size: 14px;
        color: #c4c6cc;
        display: none;
        margin-top: 1px;
        &.is-active {
            display: block;
            color: #ff9c01;
        }
    }
    a.template-name {
        color: $blueDefault;
    }
    .label-column {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        min-height: 41px;
        width: 100%;
        padding-left: 8px;
        &:hover {
            cursor: pointer;
            background: #dcdee5;
        }
        .label-name {
            margin: 4px 0 4px 4px;
            padding: 2px 6px;
            font-size: 12px;
            color: #63656e;
            border-radius: 8px;
        }
    }
    .label-select {
        width: 100%;
        margin: 5px 0 4px;
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
