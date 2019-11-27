/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
            :title="i18n.rankTitle"
            :selector-list="rankSelector"
            :label-width="400"
            :data-list="rankData"
            :data-loading="rankDataLoading"
            @onFilterClick="rankFilterChange">
        </horizontal-bar-chart>
        <div class="tab-content-area">
            <bk-tab :active.sync="activeTab" @tab-change="onTabChange">
                <bk-form form-type="inline">
                    <bk-form-item :label="i18n.atom">
                        <bk-select
                            v-model="tableAtom"
                            class="statistics-select"
                            :placeholder="i18n.selectAtom"
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
                    <bk-form-item :label="i18n.projectBeLongTo">
                        <bk-select
                            v-model="tableProject"
                            class="statistics-select"
                            :placeholder="i18n.selectProject"
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
                    <bk-form-item :label="i18n.rankBeLongTo">
                        <bk-select
                            v-model="tableCategory"
                            class="statistics-select"
                            :placeholder="i18n.selectCategory"
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
                        @page-change="handlePageChange">
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
    import '@/utils/i18n.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import HorizontalBarChart from './HorizontalBarChart.vue'
    import NoData from '@/components/common/base/NoData.vue'

    const TABS = [
        {
            id: 'atom_template',
            name: gettext('流程引用详情')
        },
        {
            id: 'atom_instance',
            name: gettext('任务执行详情')
        }
    ]

    const TABLE_COLUMN = {
        atom_template: [
            {
                label: gettext('流程ID'),
                prop: 'templateId',
                sortable: true,
                width: 100
            },
            {
                label: gettext('流程名称'),
                prop: 'templateName'
            },
            {
                label: gettext('项目'),
                prop: 'projectName'
            },
            {
                label: gettext('分类'),
                prop: 'category',
                width: 180
            },
            {
                label: gettext('创建人'),
                prop: 'creator',
                width: 120
            },
            {
                label: gettext('创建时间'),
                prop: 'createTime',
                sortable: true
            }
        ],
        atom_instance: [
            {
                label: gettext('任务ID'),
                prop: 'instanceId',
                sortable: true,
                width: 100
            },
            {
                label: gettext('任务名称'),
                prop: 'instanceName'
            },
            {
                label: gettext('项目'),
                prop: 'projectName'
            },
            {
                label: gettext('分类'),
                prop: 'category',
                width: 180
            },
            {
                label: gettext('创建人'),
                prop: 'creator',
                width: 120
            },
            {
                label: gettext('创建时间'),
                prop: 'createTime',
                sortable: true
            }
        ]
    }

    const CITE_OPTIONS = [
        {
            id: 'atom_cite',
            name: gettext('流程引用次数(次)')
        },
        {
            id: 'atom_execute_times',
            name: gettext('任务执行次数(次)')
        },
        {
            id: 'atom_execute_fail_times',
            name: gettext('执行失败次数(次)')
        },
        {
            id: 'atom_avg_execute_time',
            name: gettext('执行平均耗时(秒)')
        },
        {
            id: 'atom_fail_percent',
            name: gettext('执行失败率(%)')
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
                        placeholder: gettext('请选择项目')
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
                    'limit-list': [15],
                    'show-limit': false,
                    limit: 15
                },
                i18n: {
                    rankTitle: gettext('插件统计'),
                    atom: gettext('标准插件'),
                    projectBeLongTo: gettext('所属项目'),
                    rankBeLongTo: gettext('所属分类'),
                    selectAtom: gettext('请选择标准插件'),
                    selectProject: gettext('请选择项目'),
                    selectCategory: gettext('请选择分类')
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
            ...mapActions('atomList', [
                'queryAtomData',
                'loadSingleAtomList'
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
            }
        }
    }
</script>
