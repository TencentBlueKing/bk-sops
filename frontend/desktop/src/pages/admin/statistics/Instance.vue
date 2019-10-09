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
    <div class="content-box">
        <chart-card :charts="charts"></chart-card>
        <div class="content-task-wrap" v-bkloading="{ isLoading: isInstanceTypeLoading, opacity: 1 }">
            <div class="clearfix">
                <div class="content-title">{{i18n.instanceTime}}</div>
                <div class="content-task-instance">
                    <div class="content-instance-time">
                        <!--业务选择-->
                        <bk-select
                            v-model="timeProjectSelected"
                            class="chart-select-item"
                            :popover-width="260"
                            :searchable="true"
                            :placeholder="i18n.businessPlaceholder"
                            @selected="onChangeTimeTypeBusiness"
                            @clear="onClearTimeTypeBusiness">
                            <bk-option
                                v-for="(option, index) in allProjectList"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="content-instance-time">
                        <!--分类选择-->
                        <bk-select
                            v-model="timeCategorySelected"
                            class="chart-select-item"
                            :popover-width="260"
                            :searchable="true"
                            :placeholder="i18n.categoryPlaceholder"
                            @selected="onChangeTimeTypeCategory"
                            @clear="onClearTimeTypeCategory">
                            <bk-option
                                v-for="(option, index) in categorys"
                                :key="index"
                                :id="option.value"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="content-instance-time date-scope">
                        <!--时间维度选择-->
                        <bk-select
                            v-model="choiceDate"
                            class="chart-select-item"
                            :popover-width="260"
                            :searchable="true"
                            :placeholder="i18n.choice"
                            :clearable="false"
                            @selected="onChangeTimeType">
                            <bk-option
                                v-for="(option, index) in taskDimensionArray"
                                :key="index"
                                :id="option.value"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                </div>
            </div>
            <vertical-bar-chart :time-type-list="instanceTypeData" :total-value="instanceTypeTotal"></vertical-bar-chart>
        </div>
        <table-panel :tabpanels="tabPanels"></table-panel>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import { mapActions, mapState, mapGetters } from 'vuex'
    import VerticalBarChart from './verticalBarChart.vue'
    import ChartCard from '../common/ChartCard'
    import { AnalysisMixins } from '@/mixins/js/analysisMixins.js'
    import TablePanel from '../common/TablePanel'
    import { errorHandler } from '@/utils/errorHandler.js'

    const i18n = {
        taskCategory: gettext('分类统计'),
        taskBusiness: gettext('分业务统计'),
        ownBusiness: gettext('所属项目'),
        taskDetail: gettext('任务详情'),
        executionName: gettext('归档任务耗时'),
        timeLimit: gettext('时间范围'),
        choiceCategory: gettext('分类'),
        choiceBusiness: gettext('选择项目'),
        instanceTime: gettext('分时间统计'),
        day: gettext('天'),
        categoryPlaceholder: gettext('请选择类别'),
        businessPlaceholder: gettext('请选择业务'),
        choiceAllCategory: gettext('全部分类'),
        choiceAllBusiness: gettext('全部项目'),
        instanceName: gettext('任务名称'),
        createTime: gettext('创建时间'),
        creator: gettext('创建人'),
        atomTotal: gettext('标准插件数'),
        subprocessTotal: gettext('子流程数'),
        gatewaysTotal: gettext('网关数'),
        category: gettext('分类'),
        month: gettext('月'),
        executeTime: gettext('耗时(秒)'),
        instanceId: gettext('任务ID')
    }

    export default {
        name: 'StatisticsInstance',
        components: {
            ChartCard,
            VerticalBarChart,
            TablePanel
        },
        mixins: [AnalysisMixins],
        props: ['timeRange'],
        data () {
            return {
                i18n: i18n,
                projectId: undefined,
                category: undefined,
                isInstanceLoading: true,
                isBuinsessLoading: true,
                isDetailsLoading: true,
                isNodeLoading: true,
                taskPlotData: [],
                ownBusinessData: [],
                instanceTypeData: [],
                nodeData: [],
                nodeTotal: 0,
                taskTotal: 0,
                ownBusinessTotal: 0,
                nodePageIndex: 1,
                nodeLimit: 15,
                nodeOrderBy: '-instanceId',
                detailsOrderBy: '-instanceId',
                tabName: 'taskDetails',
                nodePagination: {
                    // 分页操作
                    limit: this.nodeLimit,
                    pageIndex: this.nodePageIndex,
                    pageArray: this.dataTablePageArray // 公共js文件获取
                },
                nodeColumns: [
                    {
                        prop: 'instanceId',
                        label: i18n.instanceId,
                        width: '100',
                        sortable: 'custom',
                        align: 'center'
                    },
                    {
                        prop: 'instanceName',
                        label: i18n.instanceName,
                        width: '285',
                        title: 'instanceName',
                        formatter: (row, column, cellValue, index) => {
                            return `<a class="template-router" target="_blank" href="${this.site_url}taskflow/execute/${row.businessId}/?instance_id=${row.instanceId}">${row.instanceName}</a>`
                        }
                    },
                    {
                        prop: 'businessName', // 识别id
                        label: i18n.ownBusiness, // 表头显示名称
                        align: 'center' // 对其格式，可选（right，left，center）
                    },
                    {
                        prop: 'category',
                        label: i18n.category,
                        align: 'center'
                    },
                    {
                        prop: 'creator',
                        label: i18n.creator,
                        align: 'center'
                    },
                    {
                        prop: 'createTime',
                        label: i18n.createTime,
                        align: 'center',
                        width: 210
                    },
                    {
                        prop: 'atomTotal',
                        label: i18n.atomTotal,
                        sortable: 'custom',
                        align: 'center'
                    },
                    {
                        prop: 'subprocessTotal',
                        label: i18n.subprocessTotal,
                        sortable: 'custom',
                        align: 'center'
                    },
                    {
                        prop: 'gatewaysTotal',
                        label: i18n.gatewaysTotal,
                        sortable: 'custom',
                        align: 'center'
                    }
                ],
                detailsData: [],
                detailsTotal: 0,
                detailsPageIndex: 1,
                detailsLimit: 15,
                detailsPagination: {
                    limit: this.detailsLimit,
                    pageIndex: this.detailsPageIndex,
                    pageArray: this.dataTablePageArray
                },
                taskDimensionArray: [
                    {
                        name: i18n.day,
                        value: 'day'
                    },
                    {
                        name: i18n.month,
                        value: 'month'
                    }
                ],
                detailsColumns: [
                    {
                        prop: 'instanceId',
                        label: i18n.instanceId,
                        width: '100',
                        sortable: 'custom',
                        align: 'center'
                    },
                    {
                        prop: 'instanceName',
                        label: i18n.instanceName,
                        title: 'instanceName',
                        formatter: (row, column, cellValue, index) => {
                            return `<a class="template-router" target="_blank" href="${this.site_url}taskflow/execute/${row.businessId}/?instance_id=${row.instanceId}">${row.instanceName}</a>`
                        }
                    },
                    {
                        prop: 'businessName',
                        label: i18n.ownBusiness,
                        align: 'center'
                    },
                    {
                        prop: 'category',
                        label: i18n.category,
                        align: 'center'
                    },
                    {
                        prop: 'creator',
                        label: i18n.creator,
                        align: 'center'
                    },
                    {
                        prop: 'createTime',
                        label: i18n.createTime,
                        align: 'center'
                    },
                    {
                        prop: 'executeTime',
                        label: i18n.executeTime,
                        sortable: 'custom',
                        align: 'center'
                    }
                ],
                selectedProject: '',
                selectedCategory: '',
                categoryTime: [],
                choiceBusiness: undefined,
                tableTime: [],
                businessTime: [],
                choiceCategory: '',
                choiceTimeTypeName: '',
                choiceTimeType: 'day',
                choiceTimeTypeCategory: undefined,
                choiceTimeTypeBusiness: undefined,
                isInstanceTypeLoading: false,
                instanceTypeTotal: 0,
                taskProjectSelected: 'all',
                timeProjectSelected: 'all',
                taskCategorySelected: 'all',
                choiceDate: 'day',
                timeCategorySelected: ''
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url,
                categorys: state => state.categorys
            }),
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            charts () {
                const charts = [
                    {
                        selects: [
                            {
                                model: this.businessSelected,
                                placeholder: this.i18n.businessPlaceholder,
                                clearable: true,
                                searchable: true,
                                onSelected: this.onInstanceCategory,
                                onClear: this.onClearInstanceCategory,
                                options: this.allBusinessList,
                                option: {
                                    key: 'cc_id',
                                    name: 'cc_name'
                                }
                            }
                        ],
                        title: this.i18n.taskCategory,
                        dimensionList: this.taskPlotData,
                        totalValue: this.taskTotal,
                        isLoading: this.isInstanceLoading
                    },
                    {
                        selects: [
                            {
                                model: this.categorySelected,
                                placeholder: this.i18n.categoryPlaceholder,
                                clearable: true,
                                searchable: true,
                                onSelected: this.onSelectCategory,
                                onClear: this.onClearInstanceBizCcId,
                                options: this.categorys,
                                option: {
                                    key: 'value',
                                    name: 'name'
                                }
                            }
                        ],
                        title: this.i18n.taskBusiness,
                        dimensionList: this.ownBusinessData,
                        totalValue: this.ownBusinessTotal,
                        isLoading: this.isBuinsessLoading
                    }
                ]
                return charts
            },
            allProjectList () {
                if (this.projectList.length === 0) {
                    this.loadProjectList({ limit: 0 })
                }
                const list = tools.deepClone(this.projectList)
                list.unshift({ id: 'all', name: i18n.choiceAllBusiness })
                return list
            },
            tabPanels () {
                const tabPanels = {
                    onTabChange: this.onChangeTabPanel,
                    active: this.tabName,
                    panels: [
                        {
                            selects: [
                                {
                                    label: this.i18n.choiceBusiness,
                                    model: this.selectedCcId,
                                    placeholder: this.i18n.businessPlaceholder,
                                    clearable: true,
                                    searchable: true,
                                    onSelected: this.onSelectedBizCcId,
                                    onClear: this.onClearBizCcId,
                                    options: this.allBusinessList,
                                    option: {
                                        key: 'cc_id',
                                        name: 'cc_name'
                                    }
                                },
                                {
                                    label: this.i18n.choiceCategory,
                                    model: this.selectedCategory,
                                    placeholder: this.i18n.categoryPlaceholder,
                                    clearable: true,
                                    searchable: true,
                                    onSelected: this.onSelectedCategory,
                                    onClear: this.onClearCategory,
                                    options: this.categorys,
                                    option: {
                                        key: 'value',
                                        name: 'name'
                                    }
                                }
                            ],
                            name: 'taskDetails',
                            label: this.i18n.taskDetail,
                            data: this.nodeData,
                            total: this.nodeTotal,
                            pagination: this.nodePagination,
                            columns: this.nodeColumns,
                            loading: this.isNodeLoading,
                            handleSortChange: this.onNodeSortChange,
                            handleSizeChange: this.onNodeHandleSizeChange,
                            handleIndexChange: this.onNodeHandleIndexChange
                        },
                        {
                            selects: [
                                {
                                    label: this.i18n.choiceBusiness,
                                    model: this.selectedCcId,
                                    placeholder: this.i18n.businessPlaceholder,
                                    clearable: true,
                                    searchable: true,
                                    onSelected: this.onSelectedBizCcId,
                                    onClear: this.onClearBizCcId,
                                    options: this.allBusinessList,
                                    option: {
                                        key: 'cc_id',
                                        name: 'cc_name'
                                    }
                                },
                                {
                                    label: this.i18n.choiceCategory,
                                    model: this.selectedCategory,
                                    placeholder: this.i18n.categoryPlaceholder,
                                    clearable: true,
                                    searchable: true,
                                    onSelected: this.onSelectedCategory,
                                    onClear: this.onClearCategory,
                                    options: this.categorys,
                                    option: {
                                        key: 'value',
                                        name: 'name'
                                    }
                                }
                            ],
                            name: 'exectionTime',
                            label: this.i18n.executionName,
                            data: this.detailsData,
                            total: this.detailsTotal,
                            pagination: this.detailsPagination,
                            columns: this.detailsColumns,
                            loading: this.isDetailsLoading,
                            handleSortChange: this.detailsHandleSortChange,
                            handleSizeChange: this.onDetailsHandleSizeChange,
                            handleIndexChange: this.onDetailsHandleIndexChange
                        }
                    ]
                }
                return tabPanels
            }
        },
        watch: {
            'timeRange': function (val) {
                this.onInstanceCategory(null)
                this.onSelectCategory(null)
                this.onInstanceNode(null)
                this.onInstanceTime(null)
                this.onInstanceDetailsData(null)
            }
        },
        created () {
            this.choiceTimeTypeName = this.i18n.day
            this.onInstanceCategory(null)
            this.onSelectCategory()
            this.onInstanceTime()
            this.onInstanceNode()
        },
        methods: {
            ...mapActions('task/', [
                'queryInstanceData'
            ]),
            ...mapActions([
                'getCategorys'
            ]),
            ...mapActions('project/', [
                'loadProjectList'
            ]),
            onNodeHandleSizeChange (limit) {
                this.nodePageIndex = 1
                this.nodeLimit = limit
                this.onInstanceNode()
            },
            onNodeHandleIndexChange (pageIndex) {
                this.nodePageIndex = pageIndex
                this.onInstanceNode()
            },
            onNodeSortChange (column, prop, order) {
                order = column[0].order === 'ascending' ? '' : '-'
                this.nodeOrderBy = column[0].prop ? order + column[0].prop : '-instanceId'
                this.onInstanceNode()
            },
            onInstanceCategory (business) {
                if (business) {
                    if (business === this.choiceBusiness) {
                        // 相同的内容不需要再次查询
                        return
                    }
                    this.choiceBusiness = business
                } else if (business === undefined) {
                    if (this.choiceBusiness === undefined) {
                        return
                    }
                    this.choiceBusiness = business
                }
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'category',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        project_id: this.choiceBusiness === 'all' ? '' : this.choiceBusiness
                    })
                }
                this.statisticsCategory(data)
            },
            onClearInstanceCategory () {
                this.onInstanceCategory()
            },
            onSelectCategory (category) {
                if (category) {
                    if (category === this.choiceCategory) {
                        // 相同的内容不需要再次查询
                        return
                    }
                    this.choiceCategory = category
                } else if (category === '') {
                    if (this.choiceCategory === '') {
                        return
                    }
                    this.choiceCategory = category
                }
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'project_id',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        category: this.choiceCategory
                    })
                }
                this.statisticsProjectData(data)
            },
            onClearInstanceBizCcId () {
                this.onSelectCategory('')
            },
            onInstanceNode (value) {
                if (this.tabName !== 'taskDetails') {
                    // 防止不同界面进行触发接口调用
                    return
                }
                this.isNodeLoading = true
                if (value instanceof Array) {
                    this.resetPageIndex()
                }
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'instance_node',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        project_id: this.projectId,
                        category: this.category,
                        order_by: this.nodeOrderBy
                    }),
                    pageIndex: this.nodePageIndex,
                    limit: this.nodeLimit
                }
                try {
                    this.instanceDataTableData(data)
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onInstanceTime (value) {
                this.isInstanceTypeLoading = true
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'instance_time',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        project_id: this.choiceTimeTypeBusiness === 'all' ? '' : this.choiceTimeTypeBusiness,
                        category: this.choiceTimeTypeCategory === 'all' ? '' : this.choiceTimeTypeCategory,
                        type: this.choiceTimeType
                    })
                }
                this.instanceTimeData(data)
            },
            async instanceDataTableData (data) {
                try {
                    const templateData = await this.queryInstanceData(data)
                    switch (data.group_by) {
                        case 'instance_node':
                            this.nodeData = templateData.data.groups
                            this.nodeTotal = templateData.data.total
                            this.isNodeLoading = false
                            break
                        case 'instance_details':
                            this.detailsData = templateData.data.groups
                            this.detailsTotal = templateData.data.total
                            this.isDetailsLoading = false
                            break
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async statisticsProjectData (data) {
                this.isBuinsessLoading = true
                try {
                    const templateData = await this.queryInstanceData(data)
                    this.ownBusinessData = templateData.data.groups
                    this.ownBusinessTotal = templateData.data.total
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isBuinsessLoading = false
                }
            },
            async instanceTimeData (data) {
                try {
                    const templateData = await this.queryInstanceData(data)
                    this.instanceTypeData = templateData.data.groups
                    this.instanceTypeTotal = templateData.data.total
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isInstanceTypeLoading = false
                }
            },
            async statisticsCategory (data) {
                this.isInstanceLoading = true
                try {
                    const templateData = await this.queryInstanceData(data)
                    this.taskPlotData = templateData.data.groups
                    this.taskTotal = templateData.data.total
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isInstanceLoading = false
                }
            },
            onDetailsHandleSizeChange (limit) {
                this.detailsPageIndex = 1
                this.detailsLimit = limit
                this.onInstanceDetailsData()
            },
            onDetailsHandleIndexChange (pageIndex) {
                this.detailsPageIndex = pageIndex
                this.onInstanceDetailsData()
            },
            detailsHandleSortChange (column, prop, order) {
                order = column[0].order === 'ascending' ? '' : '-'
                this.detailsOrderBy = column[0].prop ? order + column[0].prop : '-instanceId'
                this.onInstanceDetailsData()
            },
            onInstanceDetailsData (value) {
                if (this.tabName !== 'exectionTime') {
                    // 防止不同界面进行触发接口调用
                    return
                }
                this.isDetailsLoading = true
                if (value instanceof Array) {
                    this.resetPageIndex()
                }
                try {
                    const time = this.getUTCTime(this.timeRange)
                    const data = {
                        group_by: 'instance_details',
                        conditions: JSON.stringify({
                            create_time: time[0],
                            finish_time: time[1],
                            project_id: this.projectId,
                            category: this.category,
                            order_by: this.detailsOrderBy
                        }),
                        pageIndex: this.detailsPageIndex,
                        limit: this.detailsLimit
                    }
                    this.instanceDataTableData(data)
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onChangeTabPanel (name) {
                this.tabName = name
                if (name === 'taskDetails') {
                    this.onInstanceNode()
                } else {
                    this.onInstanceDetailsData()
                }
            },
            resetPageIndex () {
                switch (this.tabName) {
                    case 'taskDetails':
                        this.nodePageIndex = 1
                        this.nodePagination.pageIndex = 1
                        break
                    case 'exectionTime':
                        this.detailsPageIndex = 1
                        this.detailsPagination.pageIndex = 1
                        break
                }
            },
            onChangeTimeTypeCategory (category, name) {
                if (category) {
                    if (category === this.choiceTimeTypeCategory) {
                        // 相同的内容不需要再次查询
                        return
                    }
                    this.choiceTimeTypeCategory = category
                } else if (category === undefined) {
                    if (this.choiceTimeTypeCategory === undefined) {
                        return
                    }
                    this.choiceTimeTypeCategory = category
                }
                this.onInstanceTime()
            },
            onClearTimeTypeCategory () {
                this.onChangeTimeTypeCategory()
            },
            onChangeTimeTypeBusiness (business, name) {
                if (business) {
                    if (business === this.choiceTimeTypeBusiness) {
                        // 相同的内容不需要再次查询
                        return
                    }
                    this.choiceTimeTypeBusiness = business
                } else if (business === undefined) {
                    if (this.choiceTimeTypeBusiness === undefined) {
                        return
                    }
                    this.choiceTimeTypeBusiness = business
                }
                this.onInstanceTime()
            },
            onClearTimeTypeBusiness () {
                this.onChangeTimeTypeBusiness()
            },
            onChangeTimeType (type, name) {
                if (type) {
                    if (type === this.choiceTimeType) {
                        // 相同的内容不需要再次查询
                        return
                    }
                    this.choiceTimeType = type
                    this.choiceTimeTypeName = name
                } else if (type === undefined) {
                    if (this.choiceTimeType === undefined) {
                        return
                    }
                    this.choiceTimeType = type
                    if (name) {
                        this.choiceTimeTypeName = name
                    }
                }
                this.onInstanceTime()
            }
        }
    }
</script>

<style lang="scss">
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
    background-color: #ffffff;
}
.content-date-picker {
    vertical-align: top;
}
.content-business-picker {
    vertical-align: top;
}
</style>
