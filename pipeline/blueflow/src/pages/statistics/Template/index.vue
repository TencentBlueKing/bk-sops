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
            <div class="content-dimesion" v-bkloading="{isLoading: isCateLoading, opacity: 1}">
                <div class="clearfix">
                    <div class="content-title">{{i18n.flowCategory}}</div>
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
                                @item-selected="onTemplateCategory">
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
                            <i :class="['bk-icon icon-angle-down', {'icon-flip': isDropdownShow}]"></i>
                        </div>
                    </div>
                </div>
                <data-statistics :dimensionList="classiFicationArray" :totalValue="ficationTotal"></data-statistics>
            </div>
            <div class="content-wrap-right" v-bkloading="{isLoading: isBussLoading, opacity: 1}">
                <div class="clearfix">
                    <div class="content-title">{{i18n.flowBusiness}}</div>
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
                                @item-selected="onTemplateBizCcId">
                            </bk-selector>
                        </div>
                        <div class="content-business-picker" @click="onTemplatePickerClick">
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
                <data-statistics :dimensionList="taskStatistArray" :totalValue="total"></data-statistics>
            </div>
        </div>
        <div class="content-process-detail">
            <bk-tab :type="'fill'" :active-name="tabName" @tab-changed="onChangeTabPanel">
                <bk-tabpanel name="processDetails" :title="i18n.node">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <span class="content-detail-label">{{i18n.timeLimit}}</span>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onTemplateNode">
                                </bk-date-range>
                            </div>
                            <div class="content-wrap-select">
                                <span class="content-detail-label">{{i18n.choiceBusiness}}</span>
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
                                    @item-selected="onSelectedBizCcId">
                                </bk-selector>
                            </div>
                            <div class="content-wrap-select">
                                <span class="content-detail-label">{{i18n.choiceCategory}}</span>
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
                                    @change="onTemplateNode"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="nodeData"
                            :total="nodeTotal"
                            :pagination="nodePagination"
                            :columns="nodeColumns"
                            :operates="nodeOperates"
                            :loading="isDetailLoading"
                            @handleSortChange="onNodeSortChange"
                            @handleSizeChange="onNodeHandleSizeChange"
                            @handleIndexChange="onNodeHandleIndexChange">
                        </data-table-pagination>
                    </div>
                </bk-tabpanel>
                <bk-tabpanel name="processReference" :title="i18n.cite">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.timeLimit}}</label>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onTemplateByCiteData">
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
                                    @change="onTemplateByCiteData"
                                    @clear="onClearBizCcId"
                                    @item-selected="onSelectedBizCcId">
                                </bk-selector>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="citeData"
                            :total="citeTotal"
                            :pagination="citePagination"
                            :columns="citeColumns"
                            :loading="isReferLoading"
                            @handleSortChange="onCiteSortChange"
                            @handleSizeChange="onCiteSizeChange"
                            @handleIndexChange="onCiteHandleIndexChange">
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
    flowCategory: gettext('流程分类'),
    flowBusiness: gettext('所属业务'),
    choiceCategory: gettext('选择分类'),
    choiceBusiness: gettext('选择业务'),
    timeLimit: gettext('时间范围'),
    node: gettext('流程详情'),
    prop: gettext('所属业务'),
    cite: gettext('流程引用'),
    choice: gettext('请选择'),
    choiceAllCategory: gettext('全部分类'),
    choiceAllBusiness: gettext('全部业务'),
    templateName: gettext('流程名称'),
    businessName: gettext('业务'),
    category: gettext('分类'),
    atomTotal: gettext('标准插件数'),
    subprocessTotal: gettext('子流程数'),
    gatewaysTotal: gettext('网关数'),
    creator: gettext('创建人'),
    createTime: gettext('创建时间'),
    history: gettext('执行历史'),
    appmakerTotal: gettext('创建轻应用数'),
    relationshipTotal: gettext('被引用为子流程数'),
    instanceTotal: gettext('创建任务数')
}

export default {
    name: 'StatisticsTemplate',
    components: {
        DataStatistics,
        DataTablePagination
    },
    mixins: [AnalysisMixins],
    data () {
        return {
            i18n: i18n,
            business: '',
            bizCcId: undefined,
            isDropdownShow: false,
            isCateLoading: true,
            isBussLoading: true,
            isReferLoading: true,
            isDetailLoading: true,
            choiceDownShow: false,
            datePickerRefShow: false,
            businessPickerRefShow: false,
            choiceBusinessName: '',
            category: undefined,
            classiFicationArray: [],
            taskStatistArray: [],
            citeData: [],
            nodeData: [],
            nodeTotal: 0,
            nodePageIndex: 1,
            nodeLimit: 15, // 每页数量
            nodeOrderBy: '-templateId',
            citeOrderBy: '-templateId',
            tabName: 'processDetails',
            nodePagination: {
                limit: this.nodeLimit,
                pageIndex: this.nodePageIndex,
                pageArray: this.dataTablePageArray
            },
            citeTotal: 0,
            citePageIndex: 1,
            citeLimit: 15,
            citePagination: {
                limit: this.citeLimit,
                pageIndex: this.citePageIndex,
                pageArray: this.dataTablePageArray // 公共js文件获取
            },
            nodeColumns: [
                {
                    prop: 'templateName',
                    label: i18n.templateName,
                    width: 285,
                    title: 'templateName',
                    formatter: (row, column, cellValue, index) => {
                        return `<a class="template-router" target="_blank" href="${this.site_url}template/edit/${row.businessId}/?template_id=${row.templateId}">${row.templateName}</a>`
                    }
                },
                {
                    prop: 'businessName', // 识别id
                    label: i18n.businessName, // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
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
                    width: 220
                }
            ],
            nodeOperates: {
                width: 160,
                isShow: true,
                data: [
                    {
                        label: i18n.history,
                        show: true,
                        cls: 'bk-button btn-size-mini ',
                        method: (index, row) => {
                            this.onInstanceHandleView(index, row)
                        }
                    }
                ]
            },
            total: 0,
            ficationTotal: 0,
            citeColumns: [
                {
                    prop: 'templateName',
                    label: i18n.templateName,
                    width: 285,
                    formatter: (row, column, cellValue, index) => {
                        return `<a class="template-router" target="_blank" href="${this.site_url}template/edit/${row.businessId}/?template_id=${row.templateId}">${row.templateName}</a>`
                    }
                },
                {
                    prop: 'templateId',
                    label: 'ID',
                    align: 'center'
                },
                {
                    prop: 'appmakerTotal',
                    label: i18n.appmakerTotal,
                    align: 'center',
                    sortable: 'custom'
                },
                {
                    prop: 'relationshipTotal',
                    label: i18n.relationshipTotal,
                    align: 'center',
                    sortable: 'custom'
                },
                {
                    prop: 'instanceTotal',
                    label: i18n.instanceTotal,
                    align: 'center',
                    sortable: 'custom'
                }
            ],
            selectedCcId: -1,
            businessSelected: 'all',
            categorySelected: 'all',
            selectedCategory: -1,
            categoryStartTime: undefined,
            categoryEndTime: undefined,
            choiceBusiness: undefined,
            tableStartTime: undefined,
            tableEndTime: undefined,
            businessStartTime: undefined,
            businessEndTime: undefined,
            choiceCategory: undefined,
            endDateMax: ''
        }
    },
    computed: {
        ...mapState({
            bizList: state => state.bizList,
            categorys: state => state.categorys,
            site_url: state => state.site_url
        }),
        businessList () {
            if (this.bizList.length === 0) {
                this.getBizList()
            }
            const list = tools.deepClone(this.bizList)
            list.unshift({cc_id: 'all', cc_name: gettext('全部业务')})
            return list
        },
        categoryList () {
            if (this.categorys.length === 0) {
                this.getCategorys()
            }
            const list = tools.deepClone(this.categorys)
            list.unshift({value: 'all', name: gettext('全部分类')})
            return list
        }
    },
    created () {
        this.getDateTime()
    },
    methods: {
        ...mapActions([
            'getBizList',
            'getCategorys'
        ]),
        ...mapActions('template/', [
            'queryTemplateData'
        ]),
        onTemplateCategory (business, name) {
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
            this.templateData(data)
        },
        onTemplateNode (oldValue = null, newValue = null) {
            if (this.tabName !== 'processDetails') {
                // 防止不同界面进行触发接口调用
                return
            }
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            this.isDetailLoading = true
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
            const data = {
                group_by: 'template_node',
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
                this.templateTableData(data)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onTemplateBizCcId (category, name) {
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
            this.templateBizIdData(data)
        },
        async templateBizIdData (data) {
            this.isBussLoading = true
            try {
                const templateData = await this.queryTemplateData(data)
                this.taskStatistArray = templateData.data.groups
                this.total = templateData.data.total
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.isBussLoading = false
            }
        },
        async templateData (data) {
            this.isCateLoading = true
            try {
                const templateData = await this.queryTemplateData(data)
                this.classiFicationArray = templateData.data.groups
                this.ficationTotal = templateData.data.total
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.isCateLoading = false
            }
        },
        async templateTableData (data) {
            const templateData = await this.queryTemplateData(data)
            switch (data.group_by) {
                case 'template_node':
                    this.nodeData = templateData.data.groups
                    this.nodeTotal = templateData.data.total
                    this.isDetailLoading = false
                    break
                case 'template_cite':
                    this.citeData = templateData.data.groups
                    this.citeTotal = templateData.data.total
                    this.isReferLoading = false
                    break
            }
        },
        onTemplateByCiteData (oldValue = null, newValue = null) {
            if (this.tabName !== 'processReference') {
                // 防止不同界面进行触发接口调用
                return
            }
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            this.isReferLoading = true
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
            const data = {
                group_by: 'template_cite',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.bizCcId,
                    category: this.category,
                    order_by: this.citeOrderBy
                }),
                pageIndex: this.citePageIndex,
                limit: this.citeLimit
            }
            try {
                this.templateTableData(data)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        // 流程引用的排序
        onCiteSortChange (column, prop, order) {
            order = column[0].order === 'ascending' ? '' : '-'
            this.citeOrderBy = column[0].prop ? order + column[0].prop : '-templateId'
            this.onTemplateByCiteData()
        },
        onCiteSizeChange (limit) {
            this.citePageIndex = 1
            this.citeLimit = limit
            this.onTemplateByCiteData()
        },
        onCiteHandleIndexChange (pageIndex) {
            this.citePageIndex = pageIndex
            this.onTemplateByCiteData()
        },
        onNodeSortChange (column, prop, order) {
            order = column[0].order === 'ascending' ? '' : '-'
            this.nodeOrderBy = column[0].prop ?  order + column[0].prop : '-templateId'
            this.onTemplateNode()
        },
        onNodeHandleSizeChange (limit) {
            this.nodePageIndex = 1
            this.nodeLimit = limit
            this.onTemplateNode()
        },
        onNodeHandleIndexChange (pageIndex) {
            this.nodePageIndex = pageIndex
            this.onTemplateNode()
        },
        onChangeTabPanel (name) {
            this.tabName  = name
            if (name === 'processDetails') {
                this.onTemplateNode()
            } else {
                this.onTemplateByCiteData()
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
            date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
            const startTime = moment(date).format('YYYY-MM-DD')
            this.tableStartTime = startTime
            this.categoryStartTime = startTime
            this.businessStartTime = startTime
        },
        onInstanceHandleView (index, row) {
            window.open(this.site_url + 'taskflow/home/' + row.businessId + '/?template_id=' + row.templateId)
        },
        onDatePickerClick () {
            this.datePickerRefShow = !this.datePickerRefShow
            this.$refs.datePickerRef.pickerVisible = this.datePickerRefShow
        },
        onTemplatePickerClick () {
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
            this.onTemplateCategory(null)
        },
        onChangeBusinessTime (oldValue, newValue) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.businessStartTime = dateArray[0]
                this.businessEndTime = dateArray[1]
            }
            this.onTemplateBizCcId(null)
        },
        resetPageIndex () {
            switch (this.tabName) {
                case 'processDetails':
                    this.nodePageIndex = 1
                    this.nodePagination.pageIndex = 1
                    break
                case 'processReference':
                    this.citePageIndex = 1
                    this.citePagination.pageIndex = 1
                    break
            }
        }
    }
}
</script>

