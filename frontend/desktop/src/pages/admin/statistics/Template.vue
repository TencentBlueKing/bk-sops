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
        <div class="tab-content-area">
            <bk-tab>
                <bk-tab-panel v-bind="{ name: 'template', label: i18n.templateTitle }">
                    <bk-form form-type="inline">
                        <bk-form-item :label="i18n.projectBeLongTo">
                            <bk-select
                                v-model="tplProject"
                                class="statistics-select"
                                :placeholder="i18n.selectProject"
                                :searchable="true"
                                :clearable="true"
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
                                :searchable="true"
                                :clearable="true"
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
                    <bk-table
                        class="tab-data-table"
                        v-bkloading="{ isLoading: tplDataLoading, opacity: 1 }"
                        :data="tplData"
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

    const TABLE_COLUMN = [
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
            prop: 'projectName',
            width: 150
        },
        {
            label: gettext('分类'),
            prop: 'category',
            width: 120
        },
        {
            label: gettext('创建人'),
            prop: 'creator',
            width: 120
        },
        {
            label: gettext('插件数'),
            prop: 'atomTotal',
            sortable: true,
            width: 100
        },
        {
            label: gettext('子流程'),
            prop: 'subprocessTotal',
            sortable: true,
            width: 100
        },
        {
            label: gettext('网关数'),
            prop: 'gatewaysTotal',
            sortable: true,
            width: 100
        },
        {
            label: gettext('已执行'),
            prop: 'instanceTotal',
            sortable: true,
            width: 100
        },
        {
            label: gettext('被引用'),
            prop: 'relationshipTotal',
            sortable: true,
            width: 100
        },
        {
            label: gettext('周期任务'),
            prop: 'periodicTotal',
            sortable: true,
            width: 110
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
                tplData: [],
                tplProject: '',
                tplCategory: '',
                tplSort: '',
                tplDataLoading: true,
                tableColumn: TABLE_COLUMN,
                pagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15, 20, 30],
                    limit: 15
                },
                i18n: {
                    categoryTitle: gettext('分类统计'),
                    projectTitle: gettext('分项目统计'),
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
            },
            categoryList (val) {
                this.categorySelector[0].options = val
            }
        },
        created () {
            this.getData()
        },
        methods: {
            ...mapActions('template', [
                'queryTemplateData'
            ]),
            getData () {
                this.getCategoryData()
                this.getProjectData()
                this.getTplData()
            },
            async loadAnalysisData (query, type = '') {
                try {
                    const res = await this.queryTemplateData(query)
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
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            project_id: this.categoryDataProject
                        }
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
                        conditions: {
                            create_time: this.dateRange[0],
                            finish_time: this.dateRange[1],
                            category: this.projectDataCategory
                        }
                    }
                    this.projectData = await this.loadAnalysisData(query)
                } catch (e) {
                    errorHandler(e, this)
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
            tplFilterChange () {
                this.pagination.current = 1
                this.getTplData()
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
