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
            <div class="content-dimesion" v-bkloading="{ isLoading: isAppLicationLoading, opacity: 1 }">
                <div class="clearfix">
                    <div class="content-title">{{i18n.category}}</div>
                    <div class="content-date">
                        <div class="content-date-business">
                            <bk-select
                                v-model="businessSelected"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                @selected="onAppMakerCategory">
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
                <data-statistics :dimension-list="taskPlotData" :total-value="taskToatal"></data-statistics>
            </div>
            <div class="content-wrap-right" v-bkloading="{ isLoading: isCategoryLoading, opacity: 1 }">
                <div class="clearfix">
                    <div class="content-title">{{i18n.ownBusiness}}</div>
                    <div class="content-statistics">
                        <div class="content-business">
                            <bk-select
                                v-model="categorySelected"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.choice"
                                @selected="onAppMakerBizCcid">
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
                <data-statistics :dimension-list="ownBusinessData" :total-value="businessTotal"></data-statistics>
            </div>
        </div>
        <div class="content-process-detail">
            <bk-tab :type="'card'" :active="'applicationDetails'">
                <bk-tab-panel name="applicationDetails" :label="i18n.applicationDetails">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.applicationTime}}</label>
                                <bk-date-picker
                                    v-model="tableTime"
                                    class="bk-date-picker-common"
                                    :placeholder="i18n.choice"
                                    :type="'daterange'"
                                    @change="onAppMakerInstance">
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
                </bk-tab-panel>
            </bk-tab>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import DataStatistics from '../dataStatistics/index.vue'
    import { mapActions, mapState } from 'vuex'
    import { AnalysisMixins } from '@/mixins/js/analysisMixins.js'
    import DataTablePagination from '@/components/common/dataTable/DataTablePagination.vue'
    import { errorHandler } from '@/utils/errorHandler.js'
    import moment from 'moment-timezone'

    const i18n = {
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
                categoryTime: [],
                choiceBusiness: undefined,
                tableTime: [],
                choiceCategory: undefined,
                endDateMax: '',
                appmakerOrderBy: '-templateId',
                businessSelected: 'all',
                categorySelected: 'all',
                showClassifyDatePanel: '',
                showBusinessDatePanel: ''
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
            this.choiceBusinessName = this.i18n.choiceAllBusiness
            this.choiceCategoryName = this.i18n.choiceAllCategory
            this.onChangeCategoryTime()
            this.onChangeBusinessTime()
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
                this.onAppMakerInstance()
            },
            onAppmakerHandleIndexChange (pageIndex) {
                this.appmakerPageIndex = pageIndex
                this.onAppMakerInstance()
            },
            onAppmakerHandleSort (column, prop, order) {
                order = column[0].order === 'ascending' ? '' : '-'
                this.appmakerOrderBy = column[0].prop ? order + column[0].prop : '-templateId'
                this.onAppMakerInstance()
            },
            onAppMakerCategory (business, name) {
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
                        biz_cc_id: this.choiceBusiness === 'all' ? '' : this.choiceBusines
                    })
                }
                this.appMakerData(data)
            },
            onAppMakerBizCcid (category, name) {
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
                const time = this.getUTCTime([this.categoryTime[0], this.categoryTime[1]])
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
            onAppMakerInstance (value) {
                if (value) {
                    this.tableTime = value
                    this.resetPageIndex()
                }
                const time = this.getUTCTime([this.tableTime[0], this.tableTime[1]])
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
                const endTime = moment(date).format('YYYY-MM-DD HH:mm:ss')
                this.tableTime[1] = endTime
                this.categoryTime[1] = endTime
                this.businessTime[1] = endTime
                date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
                const startTime = moment(date).format('YYYY-MM-DD HH:mm:ss')
                this.tableTime[0] = startTime
                this.categoryTime[0] = startTime
                this.businessTime[0] = startTime
            },
            onShutTimeSelector () {
                this.showClassifyDatePanel = this.$refs.datePickerRef.showDatePanel
                this.showBusinessDatePanel = this.$refs.businessPickerRef.showDatePanel
            },
            onDatePickerClick () {
                this.showClassifyDatePanel = this.$refs.datePickerRef.showDatePanel
            },
            onInstanceClick () {
                this.showBusinessDatePanel = this.$refs.businessPickerRef.showDatePanel
            },
            onSelectedCategory (name, value) {
                if (this.category === name) {
                    return
                }
                this.category = name
                this.resetPageIndex()
                this.onAppMakerInstance()
            },
            onSelectedBizCcId (name, value) {
                if (this.bizCcId === name) {
                    return
                }
                this.bizCcId = name
                this.resetPageIndex()
                this.onAppMakerInstance()
            },
            onClearBizCcId () {
                this.selectedCcId = -1
                this.bizCcId = undefined
                this.resetPageIndex()
                this.onAppMakerInstance()
            },
            onClearCategory () {
                this.selectedCategory = -1
                this.category = undefined
                this.resetPageIndex()
                this.onAppMakerInstance()
            },
            onChangeCategoryTime (value) {
                if (value) {
                    this.categoryTime = value
                }
                this.onAppMakerCategory(null)
            },
            onChangeBusinessTime (value) {
                if (value) {
                    this.businessTime = value
                }
                this.onAppMakerBizCcid(null)
            },
            resetPageIndex () {
                this.appmakerPageIndex = 1
                this.appmakerPagination.pageIndex = 1
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
