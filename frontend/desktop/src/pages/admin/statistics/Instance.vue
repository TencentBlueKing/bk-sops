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
    <div class="statistics-template">
        <div class="bar-chart-area">
            <percentage
                :data-loading="statsDataLoading"
                :is-temp="false"
                :data-list="statsData">
            </percentage>
            <horizontal-bar-chart
                :title="$t('职能化统计')"
                :show-form="false"
                :show-popover="true"
                :data-list="commonFuncData"
                :data-loading="commonFuncLoading">
            </horizontal-bar-chart>
            <horizontal-bar-chart
                :title="$t('分类统计')"
                :selector-list="projectSelector"
                :data-list="categoryData"
                :data-loading="categoryDataLoading"
                @onClearChartFilter="categoryFilterClear"
                @onFilterClick="categoryFilterChange">
            </horizontal-bar-chart>
            <horizontal-bar-chart
                :title="$t('分项目统计')"
                :selector-list="categorySelector"
                :data-list="projectData"
                :show-popover="true"
                :data-loading="projectDataLoading"
                :biz-useage-data="bizUseageData"
                :color-block-list="colorBlockList"
                @onClearChartFilter="projectFilterClear"
                @onFilterClick="projectFilterChange">
            </horizontal-bar-chart>
        </div>
        <div class="vertical-bar-chart-area">
            <vertical-bar-chart
                :title="$t('分时间统计')"
                :selector-list="timeSelectorList"
                :data-list="timeDataList"
                :data-loading="timeDataLoading"
                :color-block-list="colorBlockList"
                @onFilterClick="timeFilterChange"
                @onClearTimeFilter="onClearTimeFilter">
            </vertical-bar-chart>
        </div>
        <div class="tab-content-area">
            <bk-tab>
                <bk-tab-panel v-bind="{ name: 'instance', label: $t('任务详情') }">
                    <bk-form form-type="inline">
                        <bk-form-item :label="$t('所属项目')">
                            <bk-select
                                v-model="instanceProject"
                                class="statistics-select"
                                :placeholder="$t('请选择项目')"
                                :searchable="true"
                                :clearable="true"
                                :disabled="projectList.length === 0"
                                @clear="instanceFilterChange"
                                @selected="instanceFilterChange">
                                <bk-option
                                    v-for="option in projectList"
                                    :key="option.id"
                                    :name="option.name"
                                    :id="option.id">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item :label="$t('所属分类')">
                            <bk-select
                                v-model="instanceCategory"
                                class="statistics-select"
                                :placeholder="$t('请选择分类')"
                                :searchable="true"
                                :clearable="true"
                                :disabled="categoryList.length === 0"
                                @clear="instanceFilterChange"
                                @selected="instanceFilterChange">
                                <bk-option
                                    v-for="option in categoryList"
                                    :key="option.id"
                                    :name="option.name"
                                    :id="option.id">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                    </bk-form>
                    <bk-table
                        class="tab-data-table"
                        v-bkloading="{ isLoading: instanceDataLoading, opacity: 1, zIndex: 100 }"
                        :data="instanceData"
                        :max-height="768"
                        :pagination="pagination"
                        @sort-change="handleSortChange"
                        @page-change="handlePageChange"
                        @page-limit-change="handlePageLimitChange">
                        <template v-for="item in tableColumn">
                            <bk-table-column
                                v-if="item.prop !== 'create_method'"
                                :key="item.prop"
                                :label="item.label"
                                :prop="item.prop"
                                :width="item.hasOwnProperty('width') ? item.width : 'auto'"
                                :min-width="item.hasOwnProperty('minWidth') ? item.minWidth : 'auto'"
                                show-overflow-tooltip
                                :render-header="renderTableHeader"
                                :sortable="item.sortable">
                                <template slot-scope="props">
                                    <a
                                        v-if="item.prop === 'instance_name'"
                                        class="table-link"
                                        target="_blank"
                                        :title="props.row.instance_name"
                                        :href="`${site_url}taskflow/execute/${props.row.project_id}/?instance_id=${props.row.instance_id}`">
                                        {{props.row.instance_name}}
                                    </a>
                                    <template v-else-if="item.prop === 'creator' && isMultiTenantMode">
                                        <bk-user-display-name :user-id="props.row.creator" />
                                    </template>
                                    <template v-else>
                                        <span :title="props.row[item.prop]">{{ props.row[item.prop] }}</span>
                                    </template>
                                </template>
                            </bk-table-column>
                            <template v-else>
                                <bk-table-column
                                    :key="item.prop"
                                    :label="item.label"
                                    :prop="item.prop"
                                    :min-width="120"
                                    show-overflow-tooltip
                                    :render-header="renderFilterHeader">
                                    <template slot-scope="props">
                                        <span :title="props.row[item.prop]">{{ props.row[item.prop] }}</span>
                                    </template>
                                </bk-table-column>
                            </template>
                        </template>
                        <div class="empty-data" slot="empty">
                            <NoData
                                :type="isSearch ? 'search-empty' : 'empty'"
                                :message="isSearch ? $t('搜索结果为空') : ''"
                                @searchClear="handleSearchClear">
                            </NoData>
                        </div>
                    </bk-table>
                </bk-tab-panel>
            </bk-tab>
            <div id="filter-popover" class="filter-popover" ref="filterPopover">
                <ul class="label-menu">
                    <li
                        class="label-menu-item"
                        v-for="item in filterList"
                        :key="item.value"
                        @click="onSwitchCheckStatus(item)">
                        <bk-checkbox :value="item.checked"></bk-checkbox>
                        {{ item.text }}
                    </li>
                </ul>
                <div class="filter-footer">
                    <span class="operat-btn" @click="onConfirmFilter">{{ $t('确定') }}</span>
                    <span class="operat-btn" @click="onResetFilter">{{ $t('重置') }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import { COLOR_BLOCK_LIST } from '@/constants/index.js'
    import Percentage from './Percentage.vue'
    import HorizontalBarChart from './HorizontalBarChart.vue'
    import VerticalBarChart from './VerticalBarChart.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import tippy from 'bk-magic-vue/lib/utils/tippy.js'
    import CancelRequest from '@/api/cancelRequest.js'

    const SELECTORS = [
        {
            id: 'project',
            options: [],
            selected: '',
            placeholder: i18n.t('请选择项目'),
            clearable: true
        },
        {
            id: 'category',
            options: [],
            selected: '',
            placeholder: i18n.t('请选择分类'),
            clearable: true
        },
        {
            id: 'time',
            options: [
                {
                    id: 'day',
                    name: i18n.tc('天', 0)
                },
                {
                    id: 'month',
                    name: i18n.t('月')
                }
            ],
            selected: 'day',
            clearable: false
        }
    ]

    const TABLE_COLUMN = [
        {
            label: i18n.t('任务ID'),
            prop: 'instance_id',
            sortable: true,
            width: 90
        },
        {
            label: i18n.t('任务名称'),
            prop: 'instance_name',
            minWidth: 200
        },
        {
            label: i18n.t('任务类型'),
            prop: 'create_method',
            minWidth: 120
        },
        {
            label: i18n.t('项目'),
            prop: 'project_name',
            width: 150
        },
        {
            label: i18n.t('分类'),
            prop: 'category',
            width: 120
        },
        {
            label: i18n.t('创建人'),
            prop: 'creator',
            width: 120
        },
        {
            label: i18n.t('创建时间'),
            prop: 'create_time',
            width: 200
        },
        {
            label: i18n.t('插件数'),
            prop: 'atom_total',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('子流程数'),
            prop: 'subprocess_total',
            sortable: true,
            width: 120
        },
        {
            label: i18n.t('网关数'),
            prop: 'gateways_total',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('耗时'),
            prop: 'elapsed_time',
            sortable: true,
            width: 100
        }
    ]

    export default {
        name: 'StatisticsIntance',
        components: {
            Percentage,
            HorizontalBarChart,
            VerticalBarChart,
            NoData
        },
        props: {
            dateRange: {
                type: Array,
                default () {
                    return ['', '']
                }
            },
            projectList: {
                type: Array,
                default () {
                    return []
                }
            },
            categoryList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            const filterList = COLOR_BLOCK_LIST.map(item => {
                return {
                    text: item.text,
                    value: item.value,
                    checked: false
                }
            })
            return {
                categoryData: [],
                categoryDataProject: '',
                categorySelector: [{
                    id: 'category',
                    options: this.categoryList,
                    placeholder: i18n.t('请选择分类')
                }],
                categoryDataLoading: true,
                projectData: [],
                projectDataCategory: '',
                projectSelector: [{
                    id: 'project',
                    options: this.projectList,
                    placeholder: i18n.t('请选择项目')
                }],
                projectDataLoading: true,
                timeSelectorList: [
                    {
                        ...SELECTORS[0],
                        options: this.projectList
                    },
                    {
                        ...SELECTORS[1],
                        options: this.categoryList
                    },
                    {
                        ...SELECTORS[2]
                    }
                ],
                timeDataProject: '',
                timeDataCategory: '',
                timeDataType: SELECTORS[2].options[0].id,
                timeDataList: [],
                timeDataLoading: true,
                instanceData: [],
                instanceProject: '',
                instanceCategory: '',
                instanceSort: '',
                instance: null,
                filterList,
                selectedFilter: [],
                instanceDataLoading: true,
                tableColumn: TABLE_COLUMN,
                colorBlockList: COLOR_BLOCK_LIST,
                statsData: [],
                statsDataLoading: true,
                commonFuncData: [],
                commonFuncLoading: true,
                bizUseageData: {},
                pagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15, 30, 50, 100],
                    limit: 15
                }
            }
        },
        computed: {
            ...mapState({
                isMultiTenantMode: state => state.isMultiTenantMode,
                site_url: state => state.site_url
            }),
            isSearch () {
                return this.instanceProject || this.instanceCategory || this.selectedFilter.length
            }
        },
        watch: {
            dateRange (val) {
                this.pagination.current = 1
                this.getData()
            },
            projectList (val) {
                this.projectSelector[0].options = val
                this.timeSelectorList[0].options = val
            },
            categoryList (val) {
                this.categorySelector[0].options = val
                this.timeSelectorList[1].options = val
            }
        },
        created () {
            this.getData()
        },
        mounted () {
            window.addEventListener('mouseup', this.handlePopoverOutSide)
            this.$nextTick(() => {
                const dom = document.querySelector('#filter-popover')
                const options = {
                    allowHTML: true,
                    content: dom,
                    placement: 'bottom',
                    theme: 'light',
                    distance: 10,
                    trigger: 'click',
                    hideOnClick: false,
                    arrow: false,
                    extCls: 'select-all-tpl-popover'
                }
                const instance = tippy('.icon-funnel', options)
                this.instance = instance.length ? instance[0] : this.instance
            })
        },
        beforeDestroy () {
            window.removeEventListener('mouseup', this.handlePopoverOutSide)
            this.instance && this.instance.destroy()
        },
        methods: {
            ...mapActions('admin', [
                'queryInstanceData',
                'queryBizUseageData'
            ]),
            getData () {
                this.getCategoryData()
                this.getProjectData()
                this.getTimeData()
                this.getTableData()
                this.getBizUseageData()
                this.getStatsData()
                this.getCommonFuncData()
            },
            async loadAnalysisData (query, type = '') {
                try {
                    const res = await this.queryInstanceData(query)
                    if (res.result) {
                        if (type === 'instance') {
                            this.pagination.count = res.data.total
                        }
                        return res.data.groups
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getCategoryData () {
                try {
                    this.categoryDataLoading = true
                    const query = {
                        group_by: 'category',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.categoryDataProject
                        }
                    }
                    this.categoryData = await this.loadAnalysisData(query)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.categoryDataLoading = false
                }
            },
            async getProjectData () {
                try {
                    this.projectDataLoading = true
                    const query = {
                        group_by: 'project_id',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            category: this.projectDataCategory
                        }
                    }
                    this.projectData = await this.loadAnalysisData(query)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectDataLoading = false
                }
            },
            async getTimeData () {
                try {
                    this.timeDataLoading = true
                    const query = {
                        group_by: 'instance_time',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.timeDataProject,
                            category: this.timeDataCategory,
                            type: this.timeDataType
                        }
                    }
                    this.timeDataList = await this.loadAnalysisData(query)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.timeDataLoading = false
                }
            },
            async getTableData () {
                try {
                    this.instanceDataLoading = true
                    const query = {
                        group_by: 'instance_node',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.instanceProject,
                            category: this.instanceCategory,
                            order_by: this.instanceSort,
                            create_method: this.selectedFilter
                        },
                        pageIndex: this.pagination.current,
                        limit: this.pagination.limit
                    }
                    if (this.instanceSort === '') {
                        delete query.conditions.order_by
                    }
                    const source = new CancelRequest()
                    query.cancelToken = source.token
                    this.instanceData = await this.loadAnalysisData(query, 'instance')
                } catch (e) {
                    console.log(e)
                } finally {
                    this.instanceDataLoading = false
                }
            },
            async getStatsData () {
                try {
                    this.statsDataLoading = true
                    const query = {
                        group_by: 'instance_biz',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1]
                        }
                    }
                    this.statsData = await this.loadAnalysisData(query)
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.statsDataLoading = false
                }
            },
            async getCommonFuncData () {
                try {
                    this.commonFuncLoading = true
                    const query = {
                        group_by: 'common_func',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1]
                        }
                    }
                    const resp = await this.loadAnalysisData(query)
                    this.commonFuncData = resp.reduce((acc, cur) => {
                        const createMethod = [
                            {
                                name: i18n.t('职能化'),
                                value: cur.common_func_cou,
                                color: '#339dff'
                            }, {
                                name: i18n.t('非职能化'),
                                value: cur.common_cou,
                                color: '#c4c6cc'
                            }
                        ]
                        acc.push({
                            name: cur.project_name,
                            value: cur.common_func_cou + cur.common_cou,
                            isTemp: true,
                            create_method: createMethod.filter(item => item.value)
                        })
                        return acc
                    }, [])
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.commonFuncLoading = false
                }
            },
            async getBizUseageData () {
                try {
                    const resp = await this.queryBizUseageData({ query: 'task' })
                    this.bizUseageData = resp.data
                } catch (error) {
                    console.warn(error)
                }
            },
            categoryFilterChange (val) {
                this.categoryDataProject = val
                this.getCategoryData()
            },
            categoryFilterClear () {
                this.projectSelector[0].selected = ''
                this.categoryDataProject = ''
                this.getCategoryData()
            },
            projectFilterChange (val) {
                this.projectDataCategory = val
                this.getProjectData()
            },
            projectFilterClear () {
                this.categorySelector[0].selected = ''
                this.projectDataCategory = ''
                this.getProjectData()
            },
            timeFilterChange (val, selector) {
                if (selector === 'project') {
                    this.timeDataProject = val
                } else if (selector === 'category') {
                    this.timeDataCategory = val
                } else {
                    const selectTime = this.timeSelectorList.slice(-1)[0]
                    selectTime.selected = val
                    this.timeDataType = val
                }
                this.getTimeData()
            },
            onClearTimeFilter () {
                this.timeSelectorList.forEach(item => {
                    item.selected = item.id === 'time' ? 'day' : ''
                })
                this.timeDataProject = ''
                this.timeDataCategory = ''
                this.timeDataType = 'day'
                this.getTimeData()
            },
            instanceFilterChange () {
                this.pagination.current = 1
                this.getTableData()
            },
            handleSearchClear () {
                this.instanceProject = ''
                this.instanceCategory = ''
                this.instanceSort = ''
                this.selectedFilter = []
                this.filterList.forEach(item => {
                    item.checked = false
                })
                this.getTimeData()
                this.getTableData()
            },
            handleSortChange (val) {
                if (val.order === 'ascending') {
                    this.instanceSort = val.prop
                } else if (val.order === 'descending') {
                    this.instanceSort = `-${val.prop}`
                } else {
                    this.instanceSort = ''
                }
                this.getTableData()
            },
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
            },
            renderFilterHeader (h, data) {
                const self = this
                return h('div', {
                    'class': 'creat-method-filter-header'
                }, [
                    h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        data.column.label
                    ]),
                    h('i', {
                        'class': {
                            'bk-icon icon-funnel': true,
                            'is-checked': self.selectedFilter.length
                        }
                    })
                ]
                )
            },
            onSwitchCheckStatus (val) {
                const selectFilter = this.filterList.find(item => item.value === val.value)
                selectFilter.checked = !selectFilter.checked
            },
            onConfirmFilter () {
                this.selectedFilter = this.filterList.reduce((acc, cur) => {
                    if (cur.checked) {
                        acc.push(cur.value)
                    }
                    return acc
                }, [])
                this.instance && this.instance.hide()
                this.pagination.current = 1
                this.getTableData()
            },
            handlePopoverOutSide (e) {
                const popoverDom = this.$refs.filterPopover
                if (popoverDom && !popoverDom.contains(e.target)) {
                    this.instance && this.instance.hide()
                }
            },
            onResetFilter () {
                this.selectedFilter = []
                this.filterList.forEach(item => {
                    item.checked = false
                })
                this.instance && this.instance.hide()
                this.pagination.current = 1
                this.getTableData()
            },
            handlePageChange (val) {
                this.pagination.current = val
                this.getTableData()
            },
            onTabChange (val) {
                this.pagination.current = 1
                this.getTableData()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getTableData()
            }
        }
    }
</script>
<style lang="scss">
    .task-method {
        .project-name {
            font-size: 14px;
            margin-bottom: 5px;
        }
    }
    #chartjs-tooltip {
        position: absolute;
        padding: 6px 12px;
        background: rgba(0, 0, 0, 0.8);
        border: none;
        border-radius: 6px;
        pointer-events: none;
        font-size: 12px;
        color: #fff;
        .tip-title {
            font: bold 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin-bottom: 5px;
            font-size: 14px;
        }
    }
    .task-method-item {
        display: flex;
        align-items: center;
        position: relative;
        margin-bottom: 3px;
        font: 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
        .color-block {
            height: 10px;
            width: 10px;
            margin-right: 4px;
            border-width: 2px;
        }
        .task-name {
            flex: 1;
            min-width: 80px;
            max-width: 120px;
            word-break: break-all;
        }
        .hide-task-name {
            position: absolute;
            left: -9999px;
            top: -9999px;
        }
        .task-num {
            min-width: 25px;
            text-align: right;
        }
        .percentage {
            color: #979ba5;
            margin-left: 5px;
            min-width: 31px;
        }
    }
    .creat-method-filter-header {
        display: flex;
        align-items: center;
        .icon-funnel {
            font-size: 14px;
            color: #c4c6cc;
            margin-left: 5px;
            cursor: pointer;
            &.is-checked {
                color: #63656e;
            }
        }
    }
    .select-all-tpl-popover {
        pointer-events: initial;
        .tippy-tooltip {
            background: #fff !important;
            padding-bottom: 0 !important;
        }
    }
    .filter-popover {
        font-size: 12px;
        .label-menu-item {
            width: 100px;
            display: flex;
            align-items: center;
            line-height: 16px;
            margin-bottom: 10px;
            padding-left: 10px;
            color: #63656e;
            cursor: pointer;
            .bk-form-checkbox {
                margin-right: 5px;
            }
        }
        .filter-footer {
            display: flex;
            height: 31px;
            border-top: 1px solid #f0f1f5;
            align-items: center;
            justify-content: center;
            color: #3a84ff;
            cursor: pointer;
            .operat-btn {
                margin-right: 10px;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>
