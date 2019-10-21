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
    <div class="statistics-template">
        <div class="bar-chart-area">
            <horizontal-bar-chart
                :title="i18n.categoryTitle"
                :selector-list="projectSelector"
                :data-list="categoryData"
                :data-loading="categoryDataLoading"
                @onFilterClick="categoryFilterChange">
            </horizontal-bar-chart>
            <horizontal-bar-chart
                :title="i18n.projectTitle"
                :selector-list="categorySelector"
                :data-list="projectData"
                :data-loading="projectDataLoading"
                @onFilterClick="projectFilterChange">
            </horizontal-bar-chart>
        </div>
        <div class="vertical-bar-chart-area">
            <vertical-bar-chart
                :title="i18n.timeTitle"
                :selector-list="timeSelectorList"
                :data-list="timeDataList"
                :data-loading="timeDataLoading"
                @onFilterClick="timeFilterChange">
            </vertical-bar-chart>
        </div>
        <div class="tab-content-area">
            <bk-tab :active.sync="activeTab" @tab-change="onTabChange">
                <bk-form form-type="inline">
                    <bk-form-item :label="i18n.projectBeLongTo">
                        <bk-select
                            v-model="tplProject"
                            class="statistics-select"
                            :placeholder="i18n.selectProject"
                            :disabled="projectList.length === 0"
                            @change="tplFilterChange">
                            <bk-option
                                v-for="option in projectList"
                                :key="option.id"
                                :name="option.name"
                                :id="option.id">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item :label="i18n.categoryBeLongTo">
                        <bk-select
                            v-model="tplCategory"
                            class="statistics-select"
                            :placeholder="i18n.selectCategory"
                            :disabled="categoryList.length === 0"
                            @change="tplFilterChange">
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
                        v-bkloading="{ isLoading: tplDataLoading, opacity: 1 }"
                        :data="tplData"
                        :pagination="pagination"
                        @sort-change="handleSortChange"
                        @page-change="handlePageChange">
                        <bk-table-column
                            v-for="item in tableColumn[activeTab]"
                            :key="item.prop"
                            :label="item.label"
                            :prop="item.prop"
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
                                    :title="props.row.templateName"
                                    :href="`${site_url}taskflow/execute/${props.row.projectId}/?instance_id=${props.row.instanceId}`">
                                    {{props.row.instanceName}}
                                </a>
                                <template v-else>{{ props.row[item.prop] }}</template>
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
    import VerticalBarChart from './VerticalBarChart.vue'
    import NoData from '@/components/common/base/NoData.vue'

    const SELECTORS = [
        {
            id: 'project',
            options: [],
            selected: '',
            placeholder: gettext('请选择项目'),
            clearable: true
        },
        {
            id: 'category',
            options: [],
            selected: '',
            placeholder: gettext('请选择分类'),
            clearable: true
        },
        {
            id: 'time',
            options: [
                {
                    id: 'day',
                    name: gettext('天')
                },
                {
                    id: 'month',
                    name: gettext('月')
                }
            ],
            selected: 'day',
            clearable: false
        }
    ]
    
    const TABS = [
        {
            id: 'instance_details',
            name: gettext('任务详情')
        },
        {
            id: 'instance_node',
            name: gettext('归档任务耗时')
        }
    ]

    const TABLE_COLUMN = {
        instance_details: [
            {
                label: gettext('任务ID'),
                prop: 'intanceId',
                sortable: true
            },
            {
                label: gettext('任务名称'),
                prop: 'instanceName'
            },
            {
                label: gettext('所属项目'),
                prop: 'projectName'
            },
            {
                label: gettext('分类'),
                prop: 'category'
            },
            {
                label: gettext('创建人'),
                prop: 'creator'
            },
            {
                label: gettext('创建时间'),
                prop: 'createTime'
            },
            {
                label: gettext('标准插件数'),
                prop: 'atomTotal',
                sortable: true
            },
            {
                label: gettext('子流程数'),
                prop: 'subprocessTotal'
            },
            {
                label: gettext('网关数'),
                prop: 'gatewaysTotal'
            }
        ],
        instance_node: [
            {
                label: gettext('任务ID'),
                prop: 'intanceId',
                sortable: true
            },
            {
                label: gettext('任务名称'),
                prop: 'instanceName'
            },
            {
                label: gettext('所属项目'),
                prop: 'projectName'
            },
            {
                label: gettext('分类'),
                prop: 'category'
            },
            {
                label: gettext('创建人'),
                prop: 'creator'
            },
            {
                label: gettext('创建时间'),
                prop: 'createTime'
            },
            {
                label: gettext('耗时'),
                prop: 'executeTime'
            }
        ]
    }

    export default {
        name: 'StatisticsIntance',
        components: {
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
            return {
                categoryData: [],
                categoryDataProject: '',
                categorySelector: [{
                    id: 'category',
                    options: this.categoryList,
                    placeholder: gettext('请选择分类')
                }],
                categoryDataLoading: true,
                projectData: [],
                projectDataCategory: '',
                projectSelector: [{
                    id: 'project',
                    options: this.projectList,
                    placeholder: gettext('请选择项目')
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
                tabs: TABS,
                activeTab: TABS[0].id,
                tplData: [],
                tplProject: '',
                tplCategory: '',
                tplSort: '-instanceId',
                tplDataLoading: true,
                tableColumn: TABLE_COLUMN,
                pagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15],
                    'show-limit': false,
                    limit: 15
                },
                i18n: {
                    categoryTitle: gettext('分类统计'),
                    projectTitle: gettext('分项目统计'),
                    timeTitle: gettext('分时间统计'),
                    templateTitle: gettext('流程详情'),
                    projectBeLongTo: gettext('所属项目'),
                    categoryBeLongTo: gettext('所属分类'),
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
        methods: {
            ...mapActions('task', [
                'queryInstanceData'
            ]),
            getData () {
                this.getCategoryData()
                this.getProjectData()
                this.getTimeData()
                this.getTableData()
            },
            async loadAnalysisData (query, type = '') {
                try {
                    const res = await this.queryInstanceData(query)
                    if (res.result) {
                        if (type === 'tpl') {
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
            async getCategoryData () {
                try {
                    this.categoryDataLoading = true
                    const query = {
                        group_by: 'category',
                        conditions: JSON.stringify({
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.categoryDataProject
                        })
                    }
                    this.categoryData = await this.loadAnalysisData(query)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.categoryDataLoading = false
                }
            },
            async getProjectData () {
                try {
                    this.projectDataLoading = true
                    const query = {
                        group_by: 'project_id',
                        conditions: JSON.stringify({
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            category: this.projectDataCategory
                        })
                    }
                    this.projectData = await this.loadAnalysisData(query)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.projectDataLoading = false
                }
            },
            async getTimeData () {
                try {
                    this.timeDataLoading = true
                    const query = {
                        group_by: 'instance_time',
                        conditions: JSON.stringify({
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project: this.timeDataProject,
                            category: this.timeDataCategory,
                            type: this.timeDataType
                        })
                    }
                    this.timeDataList = await this.loadAnalysisData(query)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.timeDataLoading = false
                }
            },
            async getTableData () {
                try {
                    this.tplDataLoading = true
                    const query = {
                        group_by: this.activeTab,
                        conditions: JSON.stringify({
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.tplProject,
                            category: this.tplCategory,
                            order_by: this.tplSort
                        }),
                        pageIndex: this.pagination.current,
                        limit: this.pagination.limit
                    }
                    this.tplData = await this.loadAnalysisData(query, 'tpl')
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.tplDataLoading = false
                }
            },
            categoryFilterChange (val) {
                this.categoryDataProject = val
                this.getCategoryData()
            },
            projectFilterChange (val) {
                this.projectDataCategory = val
                this.getProjectData()
            },
            timeFilterChange (val, selector) {
                if (selector === 'project') {
                    this.timeDataProject = val
                } else if (selector === 'category') {
                    this.timeDataCategory = val
                } else {
                    this.timeDataType = val
                }
                this.getTimeData()
            },
            tplFilterChange () {
                this.pagination.current = 1
                this.getTableData()
            },
            handleSortChange (val) {
                if (val.order === 'ascending') {
                    this.tplSort = val.prop
                } else {
                    this.tplSort = `-${val.prop}`
                }
                this.getTableData()
            },
            handlePageChange (val) {
                this.pagination.current = val
                this.getTableData()
            },
            onTabChange (val) {
                this.pagination.current = 1
                this.getTableData()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .vertical-bar-chart-area {
        margin-top: 20px;
    }
</style>
