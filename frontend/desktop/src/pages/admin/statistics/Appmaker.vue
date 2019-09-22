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
        <table-panel :tabpanels="tabPanels"></table-panel>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import ChartCard from '../common/ChartCard'
    import TablePanel from '../common/TablePanel'
    import { mapActions, mapState } from 'vuex'
    import { AnalysisMixins } from '@/mixins/js/analysisMixins.js'
    import { errorHandler } from '@/utils/errorHandler.js'

    const i18n = {
        ownBusiness: gettext('所属业务'),
        appmakerBusiness: gettext('分业务统计'),
        applicationTime: gettext('轻应用创建时间'),
        applicationDetails: gettext('轻应用详情'),
        choiceCategory: gettext('分类'),
        choiceBusiness: gettext('所属业务'),
        choiceTime: gettext('选择时间'),
        categoryPlaceholder: gettext('请选择类别'),
        businessPlaceholder: gettext('请选择业务'),
        atom: gettext('标准插件'),
        choiceAllCategory: gettext('全部分类'),
        choiceAllBusiness: gettext('全部业务'),
        templateName: gettext('轻应用名称'),
        createTime: gettext('创建时间'),
        editTime: gettext('更新时间'),
        creator: gettext('创建人'),
        category: gettext('分类'),
        appmakerCategory: gettext('分类统计'),
        instanceTotal: gettext('创建任务数')
    }

    export default {
        name: 'StatisticsAppmaker',
        components: {
            ChartCard,
            TablePanel
        },
        mixins: [AnalysisMixins],
        props: ['timeRange'],
        data () {
            return {
                i18n: i18n,
                choiceBusinessName: '',
                choiceCategoryName: '',
                isAppLicationLoading: true,
                isCategoryLoading: true,
                isAppmakerLoading: true,
                time: [0, 0],
                taskPlotData: [],
                ownBusinessData: [],
                templateData: [],
                taskToatal: 0,
                businessTotal: 0,
                tabName: 'appmakerDetails',
                atom: '',
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
                        prop: 'category',
                        label: i18n.category,
                        align: 'center'
                    },
                    {
                        prop: 'creator',
                        label: i18n.creator,
                        align: 'center',
                        formatter: (row, column, cellValue) => {
                            return `<span>${row.creator || '--'}</span>`
                        }
                    },
                    {
                        prop: 'createTime',
                        label: i18n.createTime,
                        align: 'center'
                    },
                    {
                        prop: 'instanceTotal',
                        label: i18n.instanceTotal,
                        sortable: 'custom',
                        align: 'center'
                    }
                ],
                endDateMax: '',
                appmakerOrderBy: '-templateId'
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url
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
                                onSelected: this.onAppMakerCategory,
                                onClear: this.onClearAppMakerCategory,
                                options: this.businessList,
                                option: {
                                    key: 'cc_id',
                                    name: 'cc_name'
                                }
                            }
                        ],
                        title: this.i18n.appmakerCategory,
                        dimensionList: this.taskPlotData,
                        totalValue: this.taskToatal,
                        isLoading: this.isAppLicationLoading
                    },
                    {
                        selects: [
                            {
                                model: this.categorySelected,
                                placeholder: this.i18n.categoryPlaceholder,
                                clearable: true,
                                searchable: true,
                                onSelected: this.onAppMakerBizCcid,
                                onClear: this.onClearAppMakerBizCcid,
                                options: this.categoryList,
                                option: {
                                    key: 'value',
                                    name: 'name'
                                }
                            }
                        ],
                        title: this.i18n.appmakerBusiness,
                        dimensionList: this.ownBusinessData,
                        totalValue: this.businessTotal,
                        isLoading: this.isCategoryLoading
                    }
                ]
                return charts
            },
            tabPanels () {
                const tabPanels = {
                    onTabChange: () => {},
                    active: 'applicationDetails',
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
                            name: 'applicationDetails',
                            label: this.i18n.applicationDetails,
                            data: this.appmakerData,
                            total: this.appmakerTotal,
                            pagination: this.appmakerPagination,
                            columns: this.appmakerColumns,
                            loading: this.isAppmakerLoading,
                            handleSortChange: this.onAppmakerHandleSort,
                            handleSizeChange: this.onAppmakerHandleSizeChange,
                            handleIndexChange: this.onAppmakerHandleIndexChange
                        }
                    ]
                }
                return tabPanels
            }
        },
        watch: {
            timeRange (val) {
                this.onAppMakerCategory(null)
                this.onAppMakerBizCcid(null)
                this.onAppMakerInstance()
            }
        },
        created () {
            this.choiceBusinessName = this.i18n.choiceAllBusiness
            this.choiceCategoryName = this.i18n.choiceAllCategory
            this.onAppMakerCategory(null)
            this.onAppMakerBizCcid(null)
            this.onAppMakerInstance()
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
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'category',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        biz_cc_id: this.choiceBusiness
                    })
                }
                this.appMakerData(data)
            },
            onClearAppMakerCategory () {
                this.onAppMakerCategory()
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
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'biz_cc_id',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        category: this.choiceCategory
                    })
                }
                this.appMakerBusinessData(data)
            },
            onClearAppMakerBizCcid () {
                this.onAppMakerBizCcid()
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
                    this.resetPageIndex()
                }
                const time = this.getUTCTime(this.timeRange)
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
            onChangeTabPanel (name) {
                this.tabName = name
                this.onAppMakerInstance()
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
