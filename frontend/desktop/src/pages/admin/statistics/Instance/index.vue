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
    <div class="content-box">
        <div class="content-wrap">
            <div class="content-dimesion" v-bkloading="{ isLoading: isInstanceLoading, opacity: 1 }">
                <div class="clearfix">
                    <div class="content-title">{{i18n.taskCategory}}</div>
                    <div class="content-date">
                        <div class="content-date-business">
                            <bk-select
                                v-model="businessSelected"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                @selected="onInstanceCategory">
                                <bk-option
                                    v-for="(option, index) in businessList"
                                    :key="index"
                                    :id="option.cc_id"
                                    :name="option.cc_name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="content-date-picker" @click="onDatePickerClick">
                            <bk-date-picker
                                ref="datePickerRef"
                                v-model="categoryTime"
                                class="bk-date-picker-common"
                                :placeholder="i18n.choice"
                                :type="'daterange'"
                                @change="onChangeCategoryTime">
                            </bk-date-picker>
                        </div>
                    </div>
                </div>
                <data-statistics :dimension-list="taskPlotData" :total-value="taskTotal"></data-statistics>
            </div>
            <div class="content-wrap-right" v-bkloading="{ isLoading: isBuinsessLoading, opacity: 1 }">
                <div class="clearfix">
                    <div class="content-title">{{i18n.ownBusiness}}</div>
                    <div class="content-statistics">
                        <div class="content-business">
                            <bk-select
                                v-model="selectedCcId"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.choice"
                                @selected="onInstanceBizCcId">
                                <bk-option
                                    v-for="(option, index) in categoryList"
                                    :key="index"
                                    :id="option.value"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="content-business-picker" @click="onInstanceClick">
                            <bk-date-picker
                                ref="businessPickerRef"
                                v-model="businessTime"
                                class="bk-date-picker-common"
                                :placeholder="i18n.choice"
                                :type="'daterange'"
                                @change="onChangeBusinessTime">
                            </bk-date-picker>
                        </div>
                    </div>
                </div>
                <data-statistics :dimension-list="ownBusinessData" :total-value="ownBusinessTotal"></data-statistics>
            </div>
        </div>
        <div class="content-task-wrap" v-bkloading="{ isLoading: isInstanceTypeLoading, opacity: 1 }">
            <div class="clearfix">
                <div class="content-title">{{i18n.instanceTime}}</div>
                <div class="content-task-instance">
                    <div class="content-instance-time">
                        <!--业务选择-->
                        <bk-select
                            v-model="timeBusinessSelected"
                            class="bk-select-inline"
                            :popover-width="260"
                            :searchable="true"
                            :placeholder="i18n.choice"
                            @selected="onChangeTimeTypeBusiness">
                            <bk-option
                                v-for="(option, index) in businessList"
                                :key="index"
                                :id="option.cc_id"
                                :name="option.cc_name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="content-instance-time">
                        <!--分类选择-->
                        <bk-select
                            v-model="timeCategorySelected"
                            class="bk-select-inline"
                            :popover-width="260"
                            :searchable="true"
                            :placeholder="i18n.choice"
                            @selected="onChangeTimeTypeCategory">
                            <bk-option
                                v-for="(option, index) in categoryList"
                                :key="index"
                                :id="option.value"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="content-date-picker" @click="onTimePickerClick">
                        <bk-date-picker
                            ref="timePickerRef"
                            v-model="timeTypeTime"
                            class="bk-date-picker-common"
                            :placeholder="i18n.choice"
                            :type="'daterange'"
                            @change="onInstanceTime">
                        </bk-date-picker>
                    </div>
                    <div class="content-instance-time date-scope">
                        <!--时间维度选择-->
                        <bk-select
                            v-model="choiceDate"
                            class="bk-select-inline"
                            :popover-width="260"
                            :searchable="true"
                            :placeholder="i18n.choice"
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
        <div class="content-process-detail">
            <bk-tab :type="'card'" :active="tabName" @tab-change="onChangeTabPanel">
                <bk-tab-panel name="taskDetails" :label="i18n.taskDetail">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.timeLimit}}</label>
                                <bk-date-picker
                                    v-model="tableTime"
                                    class="bk-date-picker-common"
                                    :placeholder="i18n.choice"
                                    :type="'daterange'"
                                    @change="onInstanceNode">
                                </bk-date-picker>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceBusiness}}</label>
                                <bk-select
                                    v-model="selectedCcId"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.choice"
                                    @clear="onClearBizCcId"
                                    @selected="onSelectedBizCcId">
                                    <bk-option
                                        v-for="(option, index) in allBusinessList"
                                        :key="index"
                                        :id="option.cc_id"
                                        :name="option.cc_name">
                                    </bk-option>
                                </bk-select>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceCategory}}</label>
                                <bk-select
                                    v-model="selectedCategory"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.choice"
                                    @clear="onClearCategory"
                                    @selected="onSelectedCategory">
                                    <bk-option
                                        v-for="(option, index) in categorys"
                                        :key="index"
                                        :id="option.value"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="nodeData"
                            :total="nodeTotal"
                            :options="dataTableOptions"
                            :pagination="nodePagination"
                            :columns="nodeColumns"
                            :loading="isNodeLoading"
                            @handleSortChange="onNodeSortChange"
                            @handleSizeChange="onNodeHandleSizeChange"
                            @handleIndexChange="onNodeHandleIndexChange">
                        </data-table-pagination>
                    </div>
                </bk-tab-panel>
                <bk-tab-panel name="exectionTime" :label="i18n.executionName">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.timeLimit}}</label>
                                <bk-date-picker
                                    class="bk-date-picker-common"
                                    v-model="tableTime"
                                    :placeholder="i18n.choice"
                                    :type="'daterange'"
                                    @change="onInstanceDetailsData">
                                </bk-date-picker>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceBusiness}}</label>
                                <bk-select
                                    v-model="selectedCcId"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.choice"
                                    @clear="onClearBizCcId"
                                    @selected="onSelectedBizCcId">
                                    <bk-option
                                        v-for="(option, index) in allBusinessList"
                                        :key="index"
                                        :id="option.cc_id"
                                        :name="option.cc_name">
                                    </bk-option>
                                </bk-select>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceCategory}}</label>
                                <bk-select
                                    v-model="selectedCategory"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.choice"
                                    @clear="onClearCategory"
                                    @selected="onSelectedCategory">
                                    <bk-option
                                        v-for="(option, index) in categorys"
                                        :key="index"
                                        :id="option.value"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="detailsData"
                            :total="detailsTotal"
                            :pagination="detailsPagination"
                            :columns="detailsColumns"
                            :loading="isDetailsLoading"
                            @handleSizeChange="onDetailsHandleSizeChange"
                            @handleIndexChange="onDetailsHandleIndexChange">
                        </data-table-pagination>
                    </div>
                </bk-tab-panel>
            </bk-tab>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import DataStatistics from '../dataStatistics/index.vue'
    import VerticalBarChart from '../verticalBarChart/index.vue'
    import { mapActions, mapState } from 'vuex'
    import { AnalysisMixins } from '@/mixins/js/analysisMixins.js'
    import DataTablePagination from '@/components/common/dataTable/DataTablePagination.vue'
    import { errorHandler } from '@/utils/errorHandler.js'
    import moment from 'moment-timezone'

    const i18n = {
        taskCategory: gettext('任务分类'),
        ownBusiness: gettext('所属业务'),
        taskDetail: gettext('任务详情'),
        executionName: gettext('执行耗时'),
        timeLimit: gettext('时间范围'),
        choiceCategory: gettext('选择分类'),
        choiceBusiness: gettext('选择业务'),
        instanceTime: gettext('时间维度'),
        day: gettext('天'),
        choice: gettext('请选择'),
        choiceAllCategory: gettext('全部分类'),
        choiceAllBusiness: gettext('全部业务'),
        instanceName: gettext('任务名称'),
        createTime: gettext('创建时间'),
        creator: gettext('创建人'),
        atomTotal: gettext('标准插件数'),
        subprocessTotal: gettext('子流程数'),
        gatewaysTotal: gettext('网关数'),
        category: gettext('分类'),
        month: gettext('月'),
        executeTime: gettext('耗时(秒)')
    }

    export default {
        name: 'StatisticsInstance',
        components: {
            DataStatistics,
            VerticalBarChart,
            DataTablePagination
        },
        mixins: [AnalysisMixins],
        data () {
            return {
                i18n: i18n,
                bizCcId: undefined,
                category: undefined,
                datePickerRefShow: false,
                businessPickerRefShow: false,
                isDropdownShow: false,
                choiceDownShow: false,
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
                        prop: 'createTime',
                        label: i18n.createTime,
                        align: 'center'
                    },
                    {
                        prop: 'creator',
                        label: i18n.creator,
                        align: 'center'
                    },
                    {
                        prop: 'category',
                        label: i18n.category,
                        align: 'center'
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
                        prop: 'executeTime',
                        label: i18n.executeTime,
                        align: 'center'
                    },
                    {
                        prop: 'creator',
                        label: i18n.creator,
                        align: 'center'
                    }
                ],
                instanceType: 'day',
                selectedCcId: '',
                selectedCategory: '',
                categoryTime: [],
                choiceBusiness: undefined,
                tableTime: [],
                businessTime: [],
                choiceCategory: '',
                endDateMax: '',
                choiceTimeTypeName: '',
                choiceTimeType: 'day',
                choiceTimeTypeCategoryName: '',
                choiceTimeTypeCategory: undefined,
                choiceTimeTypeBusinessName: '',
                choiceTimeTypeBusiness: undefined,
                timeTypeTime: [],
                isInstanceTypeLoading: false,
                instanceTypeTotal: 0,
                businessSelected: 'all',
                timeBusinessSelected: 'all',
                categorySelected: 'all',
                choiceDate: 'day',
                showClassifyDatePanel: '',
                showBusinessDatePanel: '',
                timeCategorySelected: 'all'
            }
        },
        computed: {
            ...mapState({
                allBusinessList: state => state.allBusinessList,
                categorys: state => state.categorys,
                site_url: state => state.site_url
            }),
            businessList () {
                if (this.allBusinessList.length === 0) {
                    this.getBizList(1)
                }
                const list = tools.deepClone(this.allBusinessList)
                list.unshift({ cc_id: 'all', cc_name: i18n.choiceAllBusiness })
                return list
            },
            categoryList () {
                if (this.categorys.length === 0) {
                    this.getCategorys()
                }
                const list = tools.deepClone(this.categorys)
                list.unshift({ value: 'all', name: i18n.choiceAllCategory })
                return list
            }
        },
        created () {
            this.getDateTime()
            this.choiceTimeTypeName = this.i18n.day
            this.onChangeCategoryTime()
            this.onChangeBusinessTime()
            this.onInstanceTime()
        },
        methods: {
            ...mapActions('task/', [
                'queryInstanceData'
            ]),
            ...mapActions([
                'getBizList',
                'getCategorys'
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
                const time = this.getUTCTime([this.categoryTime[0], this.categoryTime[1]])
                const data = {
                    group_by: 'category',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        biz_cc_id: this.choiceBusiness === 'all' ? '' : this.choiceBusiness
                    })
                }
                this.statisticsCategory(data)
            },
            onInstanceBizCcId (category) {
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
                const time = this.getUTCTime([this.businessTime[0], this.businessTime[1]])
                const data = {
                    group_by: 'biz_cc_id',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        category: this.choiceCategory === 'all' ? '' : this.choiceCategory
                    })
                }
                this.statisticsBizCcId(data)
            },
            onInstanceNode (value) {
                if (this.tabName !== 'taskDetails') {
                    // 防止不同界面进行触发接口调用
                    return
                }
                this.isNodeLoading = true
                if (value instanceof Array) {
                    this.tableTime = value
                    this.resetPageIndex()
                }
                const time = this.getUTCTime([this.tableTime[0], this.tableTime[1]])
                const data = {
                    group_by: 'instance_node',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        biz_cc_id: this.bizCcId,
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
                if (value) {
                    this.timeTypeTime = value
                }
                this.isInstanceTypeLoading = true
                const time = this.getUTCTime([this.timeTypeTime[0], this.timeTypeTime[1]])
                const data = {
                    group_by: 'instance_time',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        biz_cc_id: this.choiceTimeTypeBusiness === 'all' ? '' : this.choiceTimeTypeBusiness,
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
            async statisticsBizCcId (data) {
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
                    this.tableTime = value
                    this.resetPageIndex()
                }
                try {
                    const time = this.getUTCTime([this.tableTime[0], this.tableTime[1]])
                    const data = {
                        group_by: 'instance_details',
                        conditions: JSON.stringify({
                            create_time: time[0],
                            finish_time: time[1],
                            biz_cc_id: this.bizCcId,
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
            getDateTime () {
                const date = new Date()
                const endTime = moment(date).format('YYYY-MM-DD HH:mm:ss')
                this.tableTime[1] = endTime
                this.categoryTime[1] = endTime
                this.businessTime[1] = endTime
                this.timeTypeTime[1] = endTime
                date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
                const startTime = moment(date).format('YYYY-MM-DD HH:mm:ss')
                this.tableTime[0] = startTime
                this.businessTime[0] = startTime
                this.categoryTime[0] = startTime
                this.timeTypeTime[0] = startTime
            },
            onShutTimeSelector () {
                this.showClassifyDatePanel = this.$refs.datePickerRef.showDatePanel
                this.showBusinessDatePanel = this.$refs.businessPickerRef.showDatePanel
                this.choiceDownShow = this.$refs.timePickerRef.showDatePanel
            },
            onDatePickerClick () {
                this.showClassifyDatePanel = this.$refs.datePickerRef.showDatePanel
            },
            onInstanceClick () {
                this.showBusinessDatePanel = this.$refs.businessPickerRef.showDatePanel
            },
            onTimePickerClick () {
                this.choiceDownShow = this.$refs.timePickerRef.showDatePanel
            },
            onSelectedCategory (name, value) {
                if (this.category === name) {
                    return
                }
                this.category = name
                this.resetPageIndex()
                this.onChangeTabPanel(this.tabName)
            },
            onSelectedBizCcId (name, value) {
                if (this.bizCcId === name) {
                    return
                }
                this.bizCcId = name
                this.resetPageIndex()
                this.onChangeTabPanel(this.tabName)
            },
            onClearBizCcId () {
                this.selectedCcId = ''
                this.bizCcId = undefined
                this.resetPageIndex()
                this.onChangeTabPanel(this.tabName)
            },
            onClearCategory () {
                this.selectedCategory = ''
                this.category = undefined
                this.resetPageIndex()
                this.onChangeTabPanel(this.tabName)
            },
            onChangeCategoryTime (value) {
                if (value) {
                    this.categoryTime = value
                }
                this.onInstanceCategory(null)
            },
            onChangeBusinessTime (value) {
                if (value) {
                    this.businessTime = value
                }
                this.onInstanceBizCcId(null)
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
.bk-date-range {
    position: relative;
    left: 20px;
    border-right: 35px solid rgba(0,0,0,0);
}
.content-date-picker {
    vertical-align: top;
}
.content-business-picker {
    vertical-align: top;
}
</style>
