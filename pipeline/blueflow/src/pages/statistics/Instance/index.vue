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
        <div class="content-wrap">
            <div class="content-dimesion" v-bkloading="{isLoading: isInstanceLoading, opacity: 1}">
                <div class="clearfix">
                    <div class="content-title">{{i18n.taskCategory}}</div>
                    <div class="content-date">
                        <div class="content-date-business">
                            <bk-selector
                                :list="businessList"
                                :display-key="'cc_name'"
                                :setting-name="'cc_id'"
                                :search-key="'cc_name'"
                                :setting-key="'cc_id'"
                                :selected.sync="businessSelected"
                                :searchable="true"
                                :allow-clear="true"
                                @item-selected="onInstanceCategory">
                            </bk-selector>
                        </div>
                        <div class="content-date-picker" @click="onDatePickerClick">
                            <bk-date-range
                                ref="datePickerRef"
                                :quick-select="true"
                                :start-date="categoryStartTime"
                                :end-date="categoryEndTime"
                                :end-date-max="endDateMax"
                                @change="onChangeCategoryTime">
                            </bk-date-range>
                            <i :class="['bk-icon icon-angle-down', {'icon-flip': choiceDownShow}]"></i>
                        </div>
                    </div>
                </div>
                <data-statistics :dimensionList="taskPlotData" :totalValue="taskTotal"></data-statistics>
            </div>
            <div class="content-wrap-right" v-bkloading="{isLoading: isBuinsessLoading, opacity: 1}">
                <div class="clearfix">
                    <div class="content-title">{{i18n.ownBusiness}}</div>
                    <div class="content-statistics">
                        <div class="content-business">
                             <bk-selector
                                :list="categoryList"
                                :display-key="'name'"
                                :setting-name="'value'"
                                :search-key="'name'"
                                :setting-key="'value'"
                                :selected.sync="categorySelected"
                                :placeholder="i18n.choice"
                                :searchable="true"
                                :allow-clear="true"
                                @item-selected="onInstanceBizCcId">
                            </bk-selector>
                        </div>
                        <div class="content-business-picker" @click="onInstanceClick">
                            <bk-date-range
                                ref="businessPickerRef"
                                position="bottom-left"
                                :quick-select="true"
                                :start-date="businessStartTime"
                                :end-date="businessEndTime"
                                :end-date-max="endDateMax"
                                @change="onChangeBusinessTime">
                            </bk-date-range>
                            <i :class="['bk-icon icon-angle-down', {'icon-flip': choiceDownShow}]"></i>
                        </div>
                    </div>
                </div>
                <data-statistics :dimensionList="ownBusinessData" :totalValue="ownBusinessTotal"></data-statistics>
            </div>
        </div>
        <div class="content-task-wrap" v-bkloading="{isLoading: isInstanceTypeLoading, opacity: 1}">
            <div class="clearfix">
                <div class="content-title">{{i18n.instanceTime}}</div>
                <div class="content-task-instance">
                    <div class="content-instance-time">
                        <!--时间维度选择-->
                        <bk-selector
                            :list="taskDimensionArray"
                            :display-key="'name'"
                            :setting-name="'value'"
                            :search-key="'name'"
                            :setting-key="'value'"
                            :selected.sync="choiceDate"
                            :placeholder="i18n.choice"
                            :searchable="true"
                            :allow-clear="true"
                            @item-selected="onChangeTimeType">
                        </bk-selector>
                    </div>
                    <div class="content-instance-time">
                        <!--业务选择-->
                         <bk-selector
                            :list="businessList"
                            :display-key="'cc_name'"
                            :setting-name="'cc_id'"
                            :search-key="'cc_name'"
                            :setting-key="'cc_id'"
                            :selected.sync="businessSelected"
                            :searchable="true"
                            :allow-clear="true"
                            @item-selected="onChangeTimeTypeBusiness">
                        </bk-selector>
                    </div>
                    <div class="content-instance-time">
                        <!--分类选择-->
                         <bk-selector
                            :list="categoryList"
                            :display-key="'name'"
                            :setting-name="'value'"
                            :search-key="'name'"
                            :setting-key="'value'"
                            :selected.sync="categorySelected"
                            :placeholder="i18n.choice"
                            :searchable="true"
                            :allow-clear="true"
                            @item-selected="onChangeTimeTypeCategory">
                        </bk-selector>
                    </div>
                    <div class="content-date-picker">
                        <bk-date-range
                            position="bottom-left"
                            :quick-select="true"
                            :start-date="timeTypeStartTime"
                            :end-date="timeTypeEndTime"
                            :end-date-max="endDateMax"
                            @change="onInstanceTime">
                        </bk-date-range>
                        <i :class="['bk-icon icon-angle-down',{'icon-flip': choiceDownShow}]"></i>
                    </div>
                </div>
            </div>
            <data-statistics :timeTypeList="instanceTypeData" :totalValue="instanceTypeTotal"></data-statistics>
        </div>
        <div class="content-process-detail">
            <bk-tab :type="'fill'" :active-name="tabName" @tab-changed="onChangeTabPanel">
                <bk-tabpanel name="taskDetails" :title="i18n.taskDetail">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.timeLimit}}</label>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onInstanceNode">
                                </bk-date-range>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceBusiness}}</label>
                                <bk-selector
                                    :list="bizList"
                                    :display-key="'cc_name'"
                                    :setting-name="'cc_id'"
                                    :search-key="'cc_name'"
                                    :setting-key="'cc_id'"
                                    :selected.sync="selectedCcId"
                                    :placeholder="i18n.choice"
                                    :searchable="true"
                                    :allow-clear="true"
                                    @change="onInstanceNode"
                                    @clear="onClearBizCcId"
                                    @item-selected="onSelectedBizCcId">
                                </bk-selector>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceCategory}}</label>
                                <bk-selector
                                    :list="categorys"
                                    :display-key="'name'"
                                    :setting-name="'value'"
                                    :search-key="'name'"
                                    :setting-key="'value'"
                                    :selected.sync="selectedCategory"
                                    :placeholder="i18n.choice"
                                    :searchable="true"
                                    :allow-clear="true"
                                    @change="onInstanceNode"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
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
                </bk-tabpanel>
                <bk-tabpanel name="exectionTime" :title="i18n.executionName">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.timeLimit}}</label>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onInstanceDetailsData">
                                </bk-date-range>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceBusiness}}</label>
                                <bk-selector
                                    :list="bizList"
                                    :display-key="'cc_name'"
                                    :setting-name="'cc_id'"
                                    :search-key="'cc_name'"
                                    :setting-key="'cc_id'"
                                    :selected.sync="selectedCcId"
                                    :placeholder="i18n.choice"
                                    :searchable="true"
                                    :allow-clear="true"
                                    @change="onInstanceDetailsData"
                                    @clear="onClearBizCcId"
                                    @item-selected="onSelectedBizCcId">
                                </bk-selector>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.choiceCategory}}</label>
                                <bk-selector
                                    :list="categorys"
                                    :display-key="'name'"
                                    :setting-name="'value'"
                                    :search-key="'name'"
                                    :setting-key="'value'"
                                    :selected.sync="selectedCategory"
                                    :placeholder="i18n.choice"
                                    :searchable="true"
                                    :allow-clear="true"
                                    @change="onInstanceDetailsData"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
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
                </bk-tabpanel>
            </bk-tab>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import tools from '@/utils/tools.js'
import DataStatistics from '../dataStatistics/index.vue'
import {mapActions, mapState} from 'vuex'
import {AnalysisMixins} from '@/mixins/js/analysisMixins.js'
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
                    formatter: (row, column, cellValue,index) => {
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
                    formatter: (row, column, cellValue,index) => {
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
            selectedCcId: -1,
            selectedCategory: -1,
            categoryStartTime: undefined,
            categoryEndTime: undefined,
            choiceBusiness: undefined,
            tableStartTime: undefined,
            tableEndTime: undefined,
            businessStartTime: undefined,
            businessEndTime: undefined,
            choiceCategory: undefined,
            endDateMax: '',
            choiceTimeTypeName: '',
            choiceTimeType: 'day',
            choiceTimeTypeCategoryName: '',
            choiceTimeTypeCategory: undefined,
            choiceTimeTypeBusinessName: '',
            choiceTimeTypeBusiness: undefined,
            timeTypeStartTime: undefined,
            timeTypeEndTime: undefined,
            isInstanceTypeLoading: false,
            instanceTypeTotal: 0,
            businessSelected: 'all',
            categorySelected: 'all',
            choiceDate: 'day'
        }
    },
    computed: {
        ...mapState({
            bizList: state => state.bizList,
            instanceList: state => state.bizList,
            categorys: state => state.categorys,
            site_url: state => state.site_url
        }),
        businessList () {
            if (this.bizList.length === 0) {
                this.getBizList()
            }
            const list = tools.deepClone(this.bizList)
            list.unshift({cc_id: 'all', cc_name: i18n.choiceAllBusiness})
            return list
        },
        categoryList () {
            if (this.categorys.length === 0) {
                this.getCategorys()
            }
            const list = tools.deepClone(this.categorys)
            list.unshift({value: 'all', name: i18n.choiceAllCategory})
            return list
        }
    },
    created () {
        this.getDateTime()
        this.choiceTimeTypeName = this.i18n.day
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
            this.nodeOrderBy = column[0].prop ?  order + column[0].prop : '-instanceId'
            this.onInstanceNode()
        },
        onInstanceCategory (business, name) {
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
            const time = this.getUTCTime([this.categoryStartTime, this.categoryEndTime])
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
        onInstanceBizCcId (category, name) {
            if (category) {
                if (category === this.choiceCategory) {
                    // 相同的内容不需要再次查询
                    return
                }
                this.choiceCategory = category
            } else if (category === undefined) {
                if (this.choiceCategory === undefined) {
                    return
                }
                this.choiceCategory = category
            }
            const time = this.getUTCTime([this.businessStartTime, this.businessEndTime])
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
        onInstanceNode (oldValue = null, newValue = null) {
            if (this.tabName !== 'taskDetails') {
                // 防止不同界面进行触发接口调用
                return
            }
            this.isNodeLoading = true
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
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
        onInstanceTime (oldValue = null, newValue = null) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.timeTypeStartTime = dateArray[0]
                this.timeTypeEndTime = dateArray[1]
            }
            this.isInstanceTypeLoading = true
            const time = this.getUTCTime([this.timeTypeStartTime, this.timeTypeEndTime])
            const data = {
                group_by: 'instance_time',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.choiceTimeTypeBusiness === 'all' ? '' :　this.choiceTimeTypeBusiness,
                    category: this.choiceTimeTypeCategory === 'all' ? '' :　this.choiceTimeTypeCategory,
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
            this.detailsOrderBy = column[0].prop ?  order + column[0].prop : '-instanceId'
            this.onInstanceDetailsData()
        },
        onInstanceDetailsData (oldValue = null, newValue = null) {
            if (this.tabName !== 'exectionTime') {
                // 防止不同界面进行触发接口调用
                return
            }
            this.isDetailsLoading = true
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            try {
                const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
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
            date.setHours(0, 0, 0)
            const endTime = moment(date).format('YYYY-MM-DD')
            this.tableEndTime = endTime
            this.categoryEndTime = endTime
            this.businessEndTime = endTime
            this.endDateMax = endTime
            this.timeTypeEndTime = endTime
            date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
            const startTime = moment(date).format('YYYY-MM-DD')
            this.tableStartTime = startTime
            this.categoryStartTime = startTime
            this.businessStartTime = startTime
            this.timeTypeStartTime = startTime
        },
        onDatePickerClick () {
            this.datePickerRefShow = !this.datePickerRefShow
            this.$refs.datePickerRef.pickerVisible = this.datePickerRefShow
        },
        onInstanceClick () {
            this.businessPickerRefShow = !this.businessPickerRefShow
            this.$refs.businessPickerRef.pickerVisible = this.businessPickerRefShow
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
            this.selectedCcId = -1
            this.bizCcId = undefined
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        },
        onClearCategory () {
            this.selectedCategory = -1
            this.category = undefined
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        },
        onChangeCategoryTime (oldValue, newValue) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.categoryStartTime = dateArray[0]
                this.categoryEndTime = dateArray[1]
            }
            this.onInstanceCategory(null)
        },
        onChangeBusinessTime (oldValue, newValue) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.businessStartTime = dateArray[0]
                this.businessEndTime = dateArray[1]
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
