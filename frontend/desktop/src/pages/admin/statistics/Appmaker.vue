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
    <div class="statistics-appmaker">
        <div class="bar-chart-area">
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
                @onClearChartFilter="projectFilterClear"
                @onFilterClick="projectFilterChange">
            </horizontal-bar-chart>
        </div>
        <div class="tab-content-area">
            <bk-tab>
                <bk-tab-panel v-bind="{ name: 'appmaker', label: $t('轻应用详情') }">
                    <bk-form form-type="inline">
                        <bk-form-item :label="$t('所属项目')">
                            <bk-select
                                v-model="appmakerProject"
                                class="statistics-select"
                                :placeholder="$t('请选择项目')"
                                :searchable="true"
                                :clearable="true"
                                :disabled="projectList.length === 0"
                                @clear="appmakerFilterChange"
                                @selected="appmakerFilterChange">
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
                                v-model="appmakerCategory"
                                class="statistics-select"
                                :placeholder="$t('请选择分类')"
                                :searchable="true"
                                :clearable="true"
                                :disabled="categoryList.length === 0"
                                @clear="appmakerFilterChange"
                                @selected="appmakerFilterChange">
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
                        v-bkloading="{ isLoading: appmakerDataLoading, opacity: 1, zIndex: 100 }"
                        :data="appmakerData"
                        :max-height="708"
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
                                <router-link
                                    v-if="item.prop === 'template_name'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.template_name"
                                    :to="getExecuteHistoryUrl(props.row)">
                                    {{props.row.template_name}}
                                </router-link>
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

    const TABLE_COLUMN = [
        {
            label: i18n.t('轻应用名称'),
            prop: 'template_name'
        },
        {
            label: i18n.t('项目'),
            prop: 'project_name'
        },
        {
            label: i18n.t('分类'),
            prop: 'category',
            width: 140
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
            label: i18n.t('创建任务数'),
            prop: 'instance_total',
            sortable: true,
            width: 150
        }
    ]

    export default {
        name: 'StatisticsAppmaker',
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
                appmakerData: [],
                appmakerProject: '',
                appmakerCategory: '',
                appmakerSort: '',
                appmakerDataLoading: true,
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
                return this.appmakerProject || this.appmakerCategory
            }
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
                'queryAppmakerData'
            ]),
            getData () {
                this.getCategoryData()
                this.getProjectData()
                this.getAppmakerData()
            },
            async loadAnalysisData (query, type = '') {
                try {
                    const res = await this.queryAppmakerData(query)
                    if (res.result) {
                        if (type === 'appmaker') {
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
            async getAppmakerData () {
                try {
                    this.appmakerDataLoading = true
                    const query = {
                        group_by: 'appmaker_instance',
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.appmakerProject,
                            category: this.appmakerCategory,
                            order_by: this.appmakerSort
                        },
                        pageIndex: this.pagination.current,
                        limit: this.pagination.limit
                    }
                    if (this.appmakerSort === '') {
                        delete query.conditions.order_by
                    }
                    const source = new CancelRequest()
                    query.cancelToken = source.token
                    this.appmakerData = await this.loadAnalysisData(query, 'appmaker')
                } catch (e) {
                    console.log(e)
                } finally {
                    this.appmakerDataLoading = false
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
            appmakerFilterChange () {
                this.pagination.current = 1
                this.getAppmakerData()
            },
            handleSortChange (val) {
                if (val.order === 'ascending') {
                    this.appmakerSort = val.prop
                } else if (val.order === 'descending') {
                    this.appmakerSort = `-${val.prop}`
                } else {
                    this.appmakerSort = ''
                }
                this.getAppmakerData()
            },
            getExecuteHistoryUrl (val) {
                return {
                    name: 'taskList',
                    params: { project_id: val.project_id },
                    query: { template_id: val.template_id, create_method: 'app_maker', create_info: val.appmaker_id, template_source: 'project' }
                }
            },
            handlePageChange (val) {
                this.pagination.current = val
                this.getAppmakerData()
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getAppmakerData()
            },
            handleSearchClear () {
                this.appmakerProject = ''
                this.appmakerCategory = ''
                this.appmakerFilterChange()
            }
        }
    }
</script>
