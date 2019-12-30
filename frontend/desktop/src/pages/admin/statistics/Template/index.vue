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
            <div class="content-dimesion" v-bkloading="{ isLoading: isCateLoading, opacity: 1 }">
                <div class="clearfix">
                    <div class="content-title">{{i18n.flowCategory}}</div>
                    <div class="content-date">
                        <div class="content-date-business">
                            <bk-select
                                v-model="businessSelected"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                @selected="onTemplateCategory">
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
                                class="bk-date-picker-common"
                                v-model="categoryTime"
                                :placeholder="i18n.choice"
                                :type="'daterange'"
                                @open-change="onShutTimeSelector"
                                @change="onChangeCategoryTime">
                            </bk-date-picker>
                            <!-- <i :class="['bk-icon icon-angle-down', { 'icon-flip': showClassifyDatePanel }]"></i> -->
                        </div>
                    </div>
                </div>
                <data-statistics :dimension-list="classiFicationArray" :total-value="ficationTotal"></data-statistics>
            </div>
            <div class="content-wrap-right" v-bkloading="{ isLoading: isBussLoading, opacity: 1 }">
                <div class="clearfix">
                    <div class="content-title">{{i18n.flowBusiness}}</div>
                    <div class="content-statistics">
                        <div class="content-business">
                            <bk-select
                                v-model="categorySelected"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="true"
                                :placeholder="i18n.choice"
                                @selected="onTemplateBizCcId">
                                <bk-option
                                    v-for="(option, index) in categoryList"
                                    :key="index"
                                    :id="option.value"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="content-business-picker" @click="onTemplatePickerClick">
                            <bk-date-picker
                                v-model="businessTime"
                                class="bk-date-picker-common"
                                ref="businessPickerRef"
                                :placeholder="i18n.choice"
                                :type="'daterange'"
                                @open-change="onShutTimeSelector"
                                @change="onChangeBusinessTime">
                            </bk-date-picker>
                            <!-- <i :class="['bk-icon icon-angle-down', { 'icon-flip': showBusinessDatePanel }]"></i> -->
                        </div>
                    </div>
                </div>
                <data-statistics :dimension-list="taskStatistArray" :total-value="total"></data-statistics>
            </div>
        </div>
        <div class="content-process-detail">
            <bk-tab :type="'card'" :active="tabName" @tab-change="onChangeTabPanel">
                <bk-tab-panel name="processDetails" :label="i18n.node">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <span class="content-detail-label">{{i18n.timeLimit}}</span>
                                <bk-date-picker
                                    v-model="tableTime"
                                    class="bk-date-picker-common"
                                    :type="'daterange'"
                                    @change="onTemplateNode">
                                </bk-date-picker>
                            </div>
                            <div class="content-wrap-select">
                                <span class="content-detail-label">{{i18n.choiceBusiness}}</span>
                                <bk-select
                                    v-model="selectedCcId"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.choice"
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
                                <span class="content-detail-label">{{i18n.choiceCategory}}</span>
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
                            :pagination="nodePagination"
                            :columns="nodeColumns"
                            :operates="nodeOperates"
                            :loading="isDetailLoading"
                            @handleSortChange="onNodeSortChange"
                            @handleSizeChange="onNodeHandleSizeChange"
                            @handleIndexChange="onNodeHandleIndexChange">
                        </data-table-pagination>
                    </div>
                </bk-tab-panel>
                <bk-tab-panel name="processReference" :label="i18n.cite">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.timeLimit}}</label>
                                <bk-date-picker
                                    v-model="tableTime"
                                    class="bk-date-picker-common"
                                    :type="'daterange'"
                                    @change="onTemplateByCiteData">
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
                                    @change="onTemplateByCiteData"
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
                tableTime: ['', ''],
                categoryTime: ['', ''],
                businessTime: ['', ''],
                selectedCcId: '',
                businessSelected: 'all',
                categorySelected: 'all',
                selectedCategory: '',
                choiceBusiness: '',
                choiceCategory: undefined,
                endDateMax: '',
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
                list.unshift({ cc_id: 'all', cc_name: gettext('全部业务') })
                return list
            },
            categoryList () {
                if (this.categorys.length === 0) {
                    this.getCategorys()
                }
                const list = tools.deepClone(this.categorys)
                list.unshift({ value: 'all', name: gettext('全部分类') })
                return list
            }
        },
        created () {
            this.getDateTime()
            this.onTemplateCategory(null)
            this.onTemplateBizCcId(null)
            this.onTemplateNode()
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
                    if (this.choiceBusiness === '') {
                        return
                    }
                    this.choiceBusiness = business
                }
                const time = this.getUTCTime(this.categoryTime)
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
            onTemplateNode (value) {
                if (this.tabName !== 'processDetails') {
                    // 防止不同界面进行触发接口调用
                    return
                }
                if (value) {
                    this.tableTime = value
                    this.resetPageIndex()
                }
                this.isDetailLoading = true
                const time = this.getUTCTime(this.tableTime)
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
                const time = this.getUTCTime(this.tableTime)
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
            onTemplateByCiteData (value) {
                if (this.tabName !== 'processReference') {
                    // 防止不同界面进行触发接口调用
                    return
                }
                if (Array.isArray(value)) {
                    this.tableTime = value
                    this.resetPageIndex()
                }
                this.isReferLoading = true
                const time = this.getUTCTime(this.tableTime)
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
                this.nodeOrderBy = column[0].prop ? order + column[0].prop : '-templateId'
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
                this.tabName = name
                if (name === 'processDetails') {
                    this.onTemplateNode()
                } else {
                    this.onTemplateByCiteData()
                }
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
            onInstanceHandleView (index, row) {
                window.open(this.site_url + 'taskflow/home/' + row.businessId + '/?template_id=' + row.templateId)
            },
            onShutTimeSelector () {
                this.showClassifyDatePanel = this.$refs.datePickerRef.showDatePanel
                this.showBusinessDatePanel = this.$refs.businessPickerRef.showDatePanel
            },
            onDatePickerClick () {
                this.showClassifyDatePanel = this.$refs.datePickerRef.showDatePanel
            },
            onTemplatePickerClick () {
                this.showBusinessDatePanel = this.$refs.businessPickerRef.showDatePanel
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
                this.categoryTime = value
                this.onTemplateCategory(null)
            },
            onChangeBusinessTime (value) {
                this.businessTime = value
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
.icon-angle-down {
    transition: all linear 0.2s;
}
.icon-flip {
    display: inline-block;
    transform: rotate(180deg);
}
.content-date-picker {
    vertical-align: top;
}
.content-business-picker {
    vertical-align: top;
}

</style>
