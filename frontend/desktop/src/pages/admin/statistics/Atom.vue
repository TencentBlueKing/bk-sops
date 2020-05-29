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
    <div class="statistics-atom">
        <horizontal-bar-chart
            :title="$t('插件统计')"
            :selector-list="rankSelector"
            :label-width="400"
            :data-list="rankData"
            :data-loading="rankDataLoading"
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
                            @change="tableFilterChange">
                            <bk-option
                                v-for="option in atomListData"
                                :key="option.id"
                                :name="option.name"
                                :id="option.id">
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
                            @change="tableFilterChange">
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
                            @change="tableFilterChange">
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
                        v-bkloading="{ isLoading: tableDataLoading, opacity: 1 }"
                        :data="tableData"
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
                            :sortable="item.sortable">
                            <template slot-scope="props">
                                <a
                                    v-if="item.prop === 'templateName'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.templateName"
                                    :href="`${site_url}template/edit/${props.row.projectId}/?template_id=${props.row.templateId}`">
                                    {{props.row.templateName}}
                                </a>
                                <a
                                    v-else-if="item.prop === 'instanceName'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.instanceName"
                                    :href="`${site_url}taskflow/execute/${props.row.projectId}/?instance_id=${props.row.instanceId}`">
                                    {{props.row.instanceName}}
                                </a>
                                <template v-else>
                                    <span :title="props.row[item.prop]">{{ props.row[item.prop] }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <div class="empty-data" slot="empty"><no-data></no-data></div>
                    </bk-table>
                </bk-tab-panel>
            </bk-tab>
        </div>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import HorizontalBarChart from './HorizontalBarChart.vue'
    import NoData from '@/components/common/base/NoData.vue'

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
                prop: 'templateId',
                sortable: true,
                width: 100
            },
            {
                label: i18n.t('流程名称'),
                prop: 'templateName'
            },
            {
                label: i18n.t('项目'),
                prop: 'projectName',
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
                prop: 'createTime',
                width: 200,
                sortable: true
            }
        ],
        atom_instance: [
            {
                label: i18n.t('任务ID'),
                prop: 'instanceId',
                sortable: true,
                width: 100
            },
            {
                label: i18n.t('任务名称'),
                prop: 'instanceName'
            },
            {
                label: i18n.t('项目'),
                prop: 'projectName'
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
                prop: 'createTime',
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
                    'limit-list': [15, 20, 30],
                    limit: 15
                }
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url
            })
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
                'loadSingleAtomList'
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
                    } else {
                        errorHandler(res, this)
                    }
                } catch (e) {
                    errorHandler(e)
                }
            },
            async getAtomList () {
                try {
                    this.atomListLoading = true
                    const res = await this.loadSingleAtomList()
                    this.atomListData = res.map(item => {
                        return {
                            id: item.code,
                            name: `${item.group_name}-${item.name}`
                        }
                    })
                } catch (e) {
                    errorHandler(e, this)
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
                    errorHandler(e, this)
                } finally {
                    this.rankDataLoading = false
                }
            },
            async getTableData () {
                try {
                    this.tableDataLoading = true
                    const query = {
                        group_by: this.activeTab,
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            component_code: this.tableAtom,
                            project_id: this.tableProject,
                            category: this.tableCategory,
                            order_by: this.tableSort
                        },
                        pageIndex: this.pagination.current,
                        limit: this.pagination.limit
                    }
                    if (this.tableSort === '') {
                        delete query.conditions.order_by
                    }
                    this.tableData = await this.loadAnalysisData(query, 'table')
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.tableDataLoading = false
                }
            },
            rankFilterChange (val, type) {
                if (type === 'cite') {
                    this.rankDataCite = val
                } else {
                    this.rankDataProject = val
                }
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
            }
        }
    }
</script>
