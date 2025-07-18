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
    <div class="statistics-atom">
        <horizontal-bar-chart
            :title="$t('插件统计')"
            :selector-list="rankSelector"
            :label-width="400"
            :data-list="rankData"
            :data-loading="rankDataLoading"
            @onClearChartFilter="rankFilterClear"
            @onFilterClick="rankFilterChange">
        </horizontal-bar-chart>
        <div class="tab-content-area">
            <bk-tab :active.sync="activeTab" @tab-change="onTabChange">
                <bk-form form-type="inline">
                    <bk-form-item :label="$t('标准插件')">
                        <bk-select
                            v-model="tableAtom"
                            class="statistics-select"
                            :placeholder="$t('请选择标准插件')"
                            :searchable="true"
                            :clearable="true"
                            :disabled="atomListData.length === 0"
                            @clear="tableFilterChange"
                            @selected="tableFilterChange">
                            <bk-option
                                v-for="option in atomListData"
                                :key="option.id + '&' + option.version"
                                :name="option.name"
                                :id="option.id + '&' + option.version + '&' + option.remote">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item :label="$t('所属项目')">
                        <bk-select
                            v-model="tableProject"
                            class="statistics-select"
                            :placeholder="$t('请选择项目')"
                            :searchable="true"
                            :clearable="true"
                            :disabled="projectList.length === 0"
                            @clear="tableFilterChange"
                            @selected="tableFilterChange">
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
                            v-model="tableCategory"
                            class="statistics-select"
                            :placeholder="$t('请选择分类')"
                            :disabled="categoryList.length === 0"
                            :searchable="true"
                            :clearable="true"
                            @clear="tableFilterChange"
                            @selected="tableFilterChange">
                            <bk-option
                                v-for="option in categoryList"
                                :key="option.id"
                                :name="option.name"
                                :id="option.id">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </bk-form>
                <bk-tab-panel v-for="tab in tabs" :key="tab.id" v-bind="{ name: tab.id, label: tab.name }">
                    <bk-table
                        class="tab-data-table"
                        v-bkloading="{ isLoading: tableDataLoading, opacity: 1, zIndex: 100 }"
                        :data="tableData"
                        :max-height="751"
                        :pagination="pagination"
                        @sort-change="handleSortChange"
                        @page-change="handlePageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column
                            v-for="item in tableColumn[activeTab]"
                            :key="item.prop"
                            :label="item.label"
                            :prop="item.prop"
                            :width="item.hasOwnProperty('width') ? item.width : 'auto'"
                            show-overflow-tooltip
                            :render-header="renderTableHeader"
                            :sortable="item.sortable">
                            <template slot-scope="props">
                                <a
                                    v-if="item.prop === 'template_name'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.template_name"
                                    :href="`${site_url}template/view/${props.row.project_id}/?template_id=${props.row.template_id}`">
                                    {{props.row.template_name}}
                                </a>
                                <a
                                    v-else-if="item.prop === 'instance_name'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.instance_name"
                                    :href="`${site_url}taskflow/execute/${props.row.project_id}/?instance_id=${props.row.instance_id}`">
                                    {{props.row.instance_name}}
                                </a>
                                <template v-else>
                                    <span :title="props.row[item.prop]">{{ props.row[item.prop] }}</span>
                                </template>
                            </template>
                        </bk-table-column>
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
        </div>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import HorizontalBarChart from './HorizontalBarChart.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import CancelRequest from '@/api/cancelRequest.js'

    const TABS = [
        {
            id: 'atom_template',
            name: i18n.t('流程引用详情')
        },
        {
            id: 'atom_instance',
            name: i18n.t('任务执行详情')
        }
    ]

    const TABLE_COLUMN = {
        atom_template: [
            {
                label: i18n.t('流程ID'),
                prop: 'template_id',
                sortable: true,
                width: 100
            },
            {
                label: i18n.t('流程名称'),
                prop: 'template_name'
            },
            {
                label: i18n.t('项目'),
                prop: 'project_name',
                width: 150
            },
            {
                label: i18n.t('分类'),
                prop: 'category',
                width: 180
            },
            {
                label: i18n.t('创建人'),
                prop: 'creator',
                width: 120
            },
            {
                label: i18n.t('创建时间'),
                prop: 'create_time',
                width: 200,
                sortable: true
            }
        ],
        atom_instance: [
            {
                label: i18n.t('任务ID'),
                prop: 'instance_id',
                sortable: true,
                width: 100
            },
            {
                label: i18n.t('任务名称'),
                prop: 'instance_name'
            },
            {
                label: i18n.t('项目'),
                prop: 'project_name'
            },
            {
                label: i18n.t('分类'),
                prop: 'category',
                width: 180
            },
            {
                label: i18n.t('创建人'),
                prop: 'creator',
                width: 120
            },
            {
                label: i18n.t('创建时间'),
                prop: 'create_time',
                sortable: true
            }
        ]
    }

    const CITE_OPTIONS = [
        {
            id: 'atom_cite',
            name: i18n.t('流程引用次数(次)')
        },
        {
            id: 'atom_execute_times',
            name: i18n.t('任务执行次数(次)')
        },
        {
            id: 'atom_execute_fail_times',
            name: i18n.t('执行失败次数(次)')
        },
        {
            id: 'atom_avg_execute_time',
            name: i18n.t('执行平均耗时(秒)')
        },
        {
            id: 'atom_fail_percent',
            name: i18n.t('执行失败率(%)')
        }
    ]

    export default {
        name: 'StatisticsTemplate',
        components: {
            HorizontalBarChart,
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
            return {
                atomListData: [],
                atomListLoading: true,
                rankData: [],
                rankSelector: [
                    {
                        id: 'cite',
                        options: CITE_OPTIONS,
                        selected: CITE_OPTIONS[0].id,
                        clearable: false
                    },
                    {
                        id: 'project',
                        options: this.projectList,
                        placeholder: i18n.t('请选择项目')
                    }
                ],
                rankDataCite: CITE_OPTIONS[0].id,
                rankDataProject: '',
                rankDataLoading: true,
                tabs: TABS,
                activeTab: TABS[0].id,
                tableData: [],
                tableAtom: '',
                tableProject: '',
                tableCategory: '',
                tableSort: '',
                tableDataLoading: true,
                tableColumn: TABLE_COLUMN,
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
                site_url: state => state.site_url
            }),
            isSearch () {
                return this.tableAtom || this.tableProject || this.tableCategory
            }
        },
        watch: {
            dateRange (val) {
                this.pagination.current = 1
                this.getData()
            },
            projectList (val) {
                this.rankSelector[1].options = val
            }
        },
        created () {
            this.getData()
            this.getAtomList()
        },
        methods: {
            ...mapActions('atomForm', [
                'loadAnalysisComponentList'
            ]),
            ...mapActions('admin', [
                'queryAtomData'
            ]),
            getData () {
                this.getRankData()
                this.getTableData()
            },
            async loadAnalysisData (query, type = '') {
                try {
                    const res = await this.queryAtomData(query)
                    if (res.result) {
                        if (type === 'table') {
                            this.pagination.count = res.data.total
                        }
                        return res.data.groups
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getAtomList () {
                try {
                    this.atomListLoading = true
                    const res = await this.loadAnalysisComponentList()
                    this.atomListData = res.data.map(item => {
                        return {
                            id: item.code,
                            name: `${item.group_name}-${item.name}-${item.version}`,
                            version: item.version,
                            remote: item.is_remote || false
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.atomListLoading = false
                }
            },
            async getRankData () {
                try {
                    this.rankDataLoading = true
                    const query = {
                        group_by: this.rankDataCite,
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.rankDataProject
                        }
                    }
                    this.rankData = await this.loadAnalysisData(query)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.rankDataLoading = false
                }
            },
            async getTableData () {
                try {
                    this.tableDataLoading = true
                    const componentCode = this.tableAtom.split('&')
                    const selectedAtom = this.atomListData.find(item => item.id === componentCode[0] && item.version === componentCode[1])
                    let isRemote = componentCode[2]
                    isRemote = isRemote === 'true' ? true : undefined
                    const query = {
                        group_by: this.activeTab,
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            component_code: componentCode[0],
                            version: selectedAtom ? selectedAtom.version : undefined,
                            project_id: this.tableProject,
                            category: this.tableCategory,
                            order_by: this.tableSort,
                            is_remote: isRemote
                        },
                        pageIndex: this.pagination.current,
                        limit: this.pagination.limit
                    }
                    if (this.tableSort === '') {
                        delete query.conditions.order_by
                    }
                    const source = new CancelRequest()
                    query.cancelToken = source.token
                    this.tableData = await this.loadAnalysisData(query, 'table')
                } catch (e) {
                    console.log(e)
                } finally {
                    this.tableDataLoading = false
                }
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
            rankFilterChange (val, type) {
                if (type === 'cite') {
                    this.rankDataCite = val
                } else {
                    this.rankDataProject = val
                }
                this.getRankData()
            },
            rankFilterClear () {
                this.rankSelector[0].selected = 'atom_cite'
                this.rankSelector[1].selected = ''
                this.rankDataCite = 'atom_cite'
                this.rankDataProject = ''
                this.getRankData()
            },
            onTabChange (tab) {
                this.pagination.current = 1
                this.tableSort = ''
                this.getTableData()
            },
            tableFilterChange () {
                this.pagination.current = 1
                this.getTableData()
            },
            handleSortChange (val) {
                if (val.order === 'ascending') {
                    this.tableSort = val.prop
                } else if (val.order === 'descending') {
                    this.tableSort = `-${val.prop}`
                } else {
                    this.tableSort = ''
                }
                this.getTableData()
            },
            handlePageChange (val) {
                this.pagination.current = val
                this.getTableData()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getTableData()
            },
            handleSearchClear () {
                this.tableAtom = ''
                this.tableProject = ''
                this.tableCategory = ''
                this.tableFilterChange()
            }
        }
    }
</script>
