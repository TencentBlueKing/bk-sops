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
            <div class="content-dimesion" v-bkloading="{isLoading: isAppLicationLoading, opacity: 1}">
                <div class="clearfix">
                    <div class="content-title">{{i18n.category}}</div>
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
                                @item-selected="onAppMarkerCategory">
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
                <data-statistics :dimensionList="taskPlotData" :totalValue="taskToatal"></data-statistics>
            </div>
            <div class="content-wrap-right" v-bkloading="{isLoading: isCategoryLoading, opacity: 1}">
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
                                :searchable="true"
                                :allow-clear="true"
                                @item-selected="onAppMarkerBizCcid">
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
                            <i :class="['bk-icon icon-angle-down', {'icon-flip': isDropdownShow}]"></i>
                        </div>
                    </div>
                </div>
                <data-statistics :dimensionList="ownBusinessData" :totalValue="businessTotal"></data-statistics>
            </div>
        </div>
        <div class="content-process-detail">
            <bk-tab :type="'fill'" :active-name="'applicationDetails'">
                <bk-tabpanel name="applicationDetails" :title="i18n.applicationDetails">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.applicationTime}}</label>
                                <bk-date-range
                                   :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onAppMarkerInstance">
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
                                    @change="onAppMarkerInstance"
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
                                    @change="onAppMarkerInstance"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="appmakerData"
                            :total="appmakerTotal"
                            :columns="appmakerColumns"
                            :pagination="appmakerPagination"
                            :loading="isAppmakerLoading"
                            @handleSortChange="onAppmakerHandleSort"
                            @handleSizeChange="onAppmakerHandleSizeChange"
                            @handleIndexChange="onAppmakerHandleIndexChange">
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
    category: gettext('轻应用分类'),
    ownBusiness: gettext('所属业务'),
    applicationTime: gettext('轻应用创建时间'),
    applicationDetails: gettext('轻应用详情'),
    choiceCategory: gettext('选择分类'),
    choiceBusiness: gettext('选择业务'),
    choiceTime: gettext('选择时间'),
    choice: gettext('请选择'),
    atom: gettext('标准插件'),
    choiceAllCategory: gettext('全部分类'),
    choiceAllBusiness: gettext('全部业务'),
    templateName: gettext('轻应用名称'),
    createTime: gettext('创建时间'),
    editTime: gettext('更新时间'),
    editor: gettext('更新人'),
    category: gettext('分类'),
    instanceTotal: gettext('创建任务数')
}

export default {
    name: 'StatisticsAppmaker',
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
            choiceBusinessName: '',
            choiceCategoryName: '',
            isDropdownShow: false,
            choiceDownShow: false,
            datePickerRefShow: false,
            businessPickerRefShow: false,
            isAppLicationLoading: true,
            isCategoryLoading: true,
            isAppmakerLoading: true,
            time: [0, 0],
            taskPlotData: [],
            ownBusinessData: [],
            nodeData: [],
            templateData: [],
            templateTotal: 0,
            taskToatal: 0,
            businessTotal: 0,
            templatePageIndex: 1,
            templateLimit: 15,
            templatePagination: {
                limit: this.templateLimit,
                pageIndex: this.templatePageIndex,
                pageArray: this.dataTablePageArray
            },
            tabName: 'appmakerDetails',
            nodePagination: {
                limit: this.nodeLimit,
                pageIndex: this.nodePageIndex,
                pageArray: this.dataTablePageArray
            },
            atom: '',
            businessTime: [0, 0],
            components: [],
            appmakerData: [],
            appmakerTotal: 0,
            appmakerPageIndex: 1,
            appmakerLimit: 15,
            appmakerPagination: {
                limit: this.appmakerLimit,
                pageIndex: this.appmakerPageIndex,
                pageArray: this.dataTablePageArray
            },
            appmakerColumns: [
                {
                    prop: 'templateName',
                    label: i18n.templateName,
                    formatter: (row, column, cellValue, index) => {
                        return `<a class="template-router" target="_blank" href="${this.site_url}appmaker/home/${row.businessId}">${row.templateName}</a>`
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
                    prop: 'editTime',
                    label: i18n.editTime,
                    align: 'center',
                    formatter: (row, column, cellValue) => {
                        return `<span>${row.editTime || '--'}</span>`
                    }
                },
                {
                    prop: 'editor',
                    label: i18n.editor,
                    align: 'center',
                    formatter: (row, column, cellValue) => {
                        return `<span>${row.editor || '--'}</span>`
                    }
                },
                {
                    prop: 'category',
                    label: i18n.category,
                    align: 'center'
                },
                {
                    prop: 'instanceTotal',
                    label: i18n.instanceTotal,
                    sortable: 'custom',
                    align: 'center'
                }
            ],
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
            appmakerOrderBy: '-templateId',
            businessSelected: 'all',
            categorySelected: 'all'
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
        this.choiceBusinessName = this.i18n.choiceAllBusiness
        this.choiceCategoryName = this.i18n.choiceAllCategory
    },
    methods: {
        ...mapActions('appmaker/', [
            'queryAppmakerData'
        ]),
        ...mapActions([
            'getBizList',
            'getCategorys'
        ]),
        handleSizeChange (limit) {
            this.limit = limit
        },
        handleIndexChange (pageIndex) {
            this.pageIndex = pageIndex
        },
        onAppmakerHandleSizeChange (limit) {
            this.appmakerPageIndex = 1
            this.appmakerLimit = limit
            this.onAppMarkerInstance()
        },
        onAppmakerHandleIndexChange (pageIndex) {
            this.appmakerPageIndex = pageIndex
            this.onAppMarkerInstance()
        },
        onAppmakerHandleSort (column, prop, order) {
            order = column[0].order === 'ascending' ? '' : '-'
            this.appmakerOrderBy = column[0].prop ?  order + column[0].prop : '-templateId'
            this.onAppMarkerInstance()
        },
        onAppMarkerCategory (business, name) {
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
                    biz_cc_id: this.choiceBusiness === 'all' ? "" : this.choiceBusines
                })
            }
            this.appMakerData(data)
        },
        onAppMarkerBizCcid (category, name) {
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
            const time = this.getUTCTime([this.categoryStartTime, this.categoryEndTime])
            const data = {
                group_by: 'biz_cc_id',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    category: this.choiceCategory === 'all' ? '' : this.choiceCategory
                })
            }
            this.appMakerBusinessData(data)
        },
        async appMakerData (data) {
            this.isAppLicationLoading = true
            try {
                const templateData = await this.queryAppmakerData(data)
                this.taskPlotData = templateData.data.groups
                this.taskToatal = templateData.data.total
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.isAppLicationLoading = false
            }
        },
        async appMakerBusinessData (data) {
            this.isCategoryLoading = true
            try {
                const templateData = await this.queryAppmakerData(data)
                this.ownBusinessData = templateData.data.groups
                this.businessTotal = templateData.data.total
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.isCategoryLoading = false
            }
        },
        async appMakerInstanceData (data) {
            this.isAppmakerLoading = true
            try {
                const templateData = await this.queryAppmakerData(data)
                switch (data.group_by) {
                    case 'appmaker_instance':
                        this.appmakerData = templateData.data.groups
                        this.appmakerTotal = templateData.data.total
                        this.isAppmakerLoading = false
                        break
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onAppMarkerInstance (oldValue = null, newValue = null) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
            const data = {
                group_by: 'appmaker_instance',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.bizCcId,
                    category: this.category,
                    order_by: this.appmakerOrderBy
                }),
                pageIndex: this.appmakerPageIndex,
                limit: this.appmakerLimit
            }
            this.appMakerInstanceData(data)
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
            this.onAppMarkerInstance()
        },
        onSelectedBizCcId (name, value) {
            if (this.bizCcId === name) {
                return
            }
            this.bizCcId = name
            this.resetPageIndex()
            this.onAppMarkerInstance()
        },
        onClearBizCcId () {
            this.selectedCcId = -1
            this.bizCcId = undefined
            this.resetPageIndex()
            this.onAppMarkerInstance()
        },
        onClearCategory () {
            this.selectedCategory = -1
            this.category = undefined
            this.resetPageIndex()
            this.onAppMarkerInstance()
        },
        onChangeCategoryTime (oldValue, newValue) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.categoryStartTime = dateArray[0]
                this.categoryEndTime = dateArray[1]
            }
            this.onAppMarkerCategory(null)
        },
        onChangeBusinessTime (oldValue, newValue) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.businessStartTime = dateArray[0]
                this.businessEndTime = dateArray[1]
            }
            this.onAppMarkerBizCcid(null)
        },
        resetPageIndex () {
            this.appmakerPageIndex = 1
            this.appmakerPagination.pageIndex = 1
        }
    }
}
</script>
