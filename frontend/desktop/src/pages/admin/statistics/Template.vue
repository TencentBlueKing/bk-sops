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
                :data-list="statsData">
            </percentage>
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
                :data-loading="projectDataLoading"
                :biz-useage-data="bizUseageData"
                @onClearChartFilter="projectFilterClear"
                @onFilterClick="projectFilterChange">
            </horizontal-bar-chart>
            <horizontal-bar-chart
                :title="$t('模板使用统计')"
                :show-form="false"
                :show-popover="true"
                :data-list="tempUsageData"
                :data-loading="tempUsageLoading">
            </horizontal-bar-chart>
            <horizontal-bar-chart
                class="topn-chart"
                :title="topnTitle"
                :show-form="false"
                :show-popover="true"
                :data-list="topnData"
                :data-loading="topnDataLoading">
            </horizontal-bar-chart>
        </div>
        <div class="tab-content-area">
            <bk-tab>
                <bk-tab-panel v-bind="{ name: 'template', label: $t('流程详情') }">
                    <bk-form form-type="inline">
                        <bk-form-item :label="$t('所属项目')">
                            <bk-select
                                v-model="tplProject"
                                class="statistics-select"
                                :placeholder="$t('请选择项目')"
                                :searchable="true"
                                :clearable="true"
                                :disabled="projectList.length === 0"
                                @clear="tplFilterChange"
                                @selected="tplFilterChange">
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
                                v-model="tplCategory"
                                class="statistics-select"
                                :placeholder="$t('请选择分类')"
                                :searchable="true"
                                :clearable="true"
                                :disabled="categoryList.length === 0"
                                @clear="tplFilterChange"
                                @selected="tplFilterChange">
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
                        v-bkloading="{ isLoading: tplDataLoading, opacity: 1, zIndex: 100 }"
                        :data="tplData"
                        :max-height="768"
                        :pagination="pagination"
                        @sort-change="handleSortChange"
                        @page-change="handlePageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column
                            v-for="item in tableColumn"
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
                                    v-else-if="item.prop === 'taskflow_total'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.taskflow_total"
                                    :href="`${site_url}taskflow/home/list/${props.row.project_id}/`">
                                    {{props.row.taskflow_total}}
                                </a>
                                <a
                                    v-else-if="item.prop === 'periodic_total'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.periodic_total"
                                    :href="`${site_url}taskflow/home/periodic/${props.row.project_id}/`">
                                    {{props.row.periodic_total}}
                                </a>
                                <template v-else>
                                    <span :title="props.row[item.prop]">{{ props.row[item.prop] }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <div class="empty-data" slot="empty">
                            <NoData
                                :type="(tplProject || tplCategory) ? 'search-empty' : 'empty'"
                                :message="(tplProject || tplCategory) ? $t('搜索结果为空') : ''"
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
    import Percentage from './Percentage.vue'
    import HorizontalBarChart from './HorizontalBarChart.vue'
    import NoData from '@/components/common/base/NoData.vue'

    const TABLE_COLUMN = [
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
            width: 120
        },
        {
            label: i18n.t('创建人'),
            prop: 'creator',
            width: 120
        },
        {
            label: i18n.t('输入变量'),
            prop: 'input_count',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('输出变量'),
            prop: 'output_count',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('插件数'),
            prop: 'atom_toal',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('子流程'),
            prop: 'subprocess_total',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('网关数'),
            prop: 'gateways_total',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('已执行'),
            prop: 'instance_total',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('被引用'),
            prop: 'relationship_total',
            sortable: true,
            width: 100
        },
        {
            label: i18n.t('普通任务'),
            prop: 'taskflow_total',
            sortable: true,
            width: 110
        },
        {
            label: i18n.t('周期任务'),
            prop: 'periodic_total',
            sortable: true,
            width: 110
        }
    ]

    export default {
        name: 'StatisticsTemplate',
        components: {
            Percentage,
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
                tplData: [],
                tplProject: '',
                tplCategory: '',
                tplSort: '',
                tplDataLoading: true,
                tableColumn: TABLE_COLUMN,
                statsData: [],
                statsDataLoading: true,
                topnTitle: i18n.t('模板执行次数TOP n', { n: 5 }),
                topnData: [],
                topnDataLoading: true,
                tempUsageData: [],
                tempUsageLoading: true,
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
            },
            categoryList (val) {
                this.categorySelector[0].options = val
            }
        },
        created () {
            this.getData()
        },
        methods: {
            ...mapActions('admin', [
                'queryTemplateData',
                'queryBizUseageData'
            ]),
            getData () {
                this.getCategoryData()
                this.getProjectData()
                this.getTplData()
                this.getBizUseageData()
                this.getStatsData()
                this.getTopnData()
                this.getTempUsageData()
            },
            async loadAnalysisData (query, type = '') {
                try {
                    const res = await this.queryTemplateData(query)
                    if (res.result) {
                        if (type === 'tpl') {
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
            async getTplData () {
                try {
                    this.tplDataLoading = true
                    const query = {
                        group_by: 'template_node',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.tplProject,
                            category: this.tplCategory,
                            order_by: this.tplSort
                        },
                        pageIndex: this.pagination.current,
                        limit: this.pagination.limit
                    }
                    if (this.tplSort === '') {
                        delete query.conditions.order_by
                    }
                    this.tplData = await this.loadAnalysisData(query, 'tpl')
                } catch (e) {
                    console.log(e)
                } finally {
                    this.tplDataLoading = false
                }
            },
            async getStatsData () {
                try {
                    this.statsDataLoading = true
                    const query = {
                        group_by: 'template_biz',
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
            async getTopnData () {
                try {
                    this.topnDataLoading = true
                    const query = {
                        group_by: 'template_execute_times',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1]
                        }
                    }
                    const resp = await this.loadAnalysisData(query)
                    this.topnTitle = i18n.t('模板执行次数TOP n', { n: resp.length })
                    this.topnData = resp.map(item => {
                        item.name = item.template_name
                        item.value = item.count
                        return item
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.topnDataLoading = false
                }
            },
            async getTempUsageData () {
                try {
                    this.tempUsageLoading = true
                    const query = {
                        group_by: 'template_execute_in_biz',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1]
                        }
                    }
                    const resp = await this.loadAnalysisData(query)
                    this.tempUsageData = resp.reduce((acc, cur) => {
                        let value = 0
                        const createMethod = cur.useage.filter(item => {
                            value += item.value
                            item.color = item.name === '已使用' ? '#339dff' : '#c4c6cc'
                            return item.value
                        })
                        acc.push({
                            name: cur.project_name,
                            value,
                            isTemp: true,
                            create_method: createMethod
                        })
                        return acc
                    }, [])
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.tempUsageLoading = false
                }
            },
            async getBizUseageData () {
                try {
                    const resp = await this.queryBizUseageData({ query: 'template' })
                    this.bizUseageData = resp.data
                } catch (error) {
                    console.warn(error)
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
            categoryFilterChange (val) {
                this.categoryDataProject = val
                this.getCategoryData()
            },
            categoryFilterClear () {
                this.projectSelector[0].checked = ''
                this.categoryDataProject = ''
                this.getCategoryData()
            },
            projectFilterChange (val) {
                this.projectDataCategory = val
                this.getProjectData()
            },
            projectFilterClear () {
                this.categorySelector[0].checked = ''
                this.projectDataCategory = ''
                this.getProjectData()
            },
            tplFilterChange () {
                this.pagination.current = 1
                this.getTplData()
            },
            handleSearchClear () {
                this.tplProject = ''
                this.tplCategory = ''
                this.tplSort = ''
                this.tplFilterChange()
            },
            handleSortChange (val) {
                if (val.order === 'ascending') {
                    this.tplSort = val.prop
                } else if (val.order === 'descending') {
                    this.tplSort = `-${val.prop}`
                } else {
                    this.tplSort = ''
                }
                this.getTplData()
            },
            handlePageChange (val) {
                this.pagination.current = val
                this.getTplData()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getTplData()
            }
        }
    }
</script>
<style lang="scss">
    .topn-chart {
        width: 100% !important;
    }
    .task-method {
        .project-name {
            font-size: 14px;
            margin-bottom: 5px;
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
        .content-wrap {
            flex: 1;
            min-width: 80px;
            max-width: 120px;
            margin-right: 10px;
            word-break: break-all;
            &.is-template {
                min-width: 140px;
                max-width: 170px;
            }
        }
        .template-id {
            color: #979ba5;
            margin-left: 3px;
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
</style>
