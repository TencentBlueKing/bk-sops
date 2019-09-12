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
                                :placeholder="i18n.businessPlaceholder"
                                @selected="onTemplateCategory"
                                @clear="onClearTemplateCategory">
                                <bk-option
                                    v-for="(option, index) in businessList"
                                    :key="index"
                                    :id="option.cc_id"
                                    :name="option.cc_name">
                                </bk-option>
                            </bk-select>
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
                                :placeholder="i18n.categoryPlaceholder"
                                @selected="onTemplateBizCcId"
                                @clear="onClearTemplateBizCcId">
                                <bk-option
                                    v-for="(option, index) in categoryList"
                                    :key="index"
                                    :id="option.value"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
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
                                <span class="content-detail-label">{{i18n.choiceBusiness}}</span>
                                <bk-select
                                    v-model="selectedCcId"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.businessPlaceholder"
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
                                <span class="content-detail-label">{{i18n.choiceCategory}}</span>
                                <bk-select
                                    v-model="selectedCategory"
                                    class="bk-select-inline"
                                    :popover-width="260"
                                    :searchable="true"
                                    :placeholder="i18n.categoryPlaceholder"
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
            </bk-tab>
        </div>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import DataStatistics from './dataStatistics.vue'
    import { mapActions, mapState } from 'vuex'
    import { AnalysisMixins } from '@/mixins/js/analysisMixins.js'
    import DataTablePagination from '@/components/common/dataTable/DataTablePagination.vue'
    import { errorHandler } from '@/utils/errorHandler.js'

    const i18n = {
        flowCategory: gettext('分类统计'),
        flowBusiness: gettext('分业务统计'),
        choiceCategory: gettext('分类'),
        choiceBusiness: gettext('所属业务'),
        timeLimit: gettext('时间范围'),
        node: gettext('流程详情'),
        prop: gettext('所属业务'),
        cite: gettext('流程引用'),
        categoryPlaceholder: gettext('请选择类别'),
        businessPlaceholder: gettext('请选择业务'),
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
        instanceTotal: gettext('创建任务数'),
        periodicTotal: gettext('创建周期任务数'),
        templateId: gettext('流程ID')
    }

    export default {
        name: 'StatisticsTemplate',
        components: {
            DataStatistics,
            DataTablePagination
        },
        mixins: [AnalysisMixins],
        props: ['timeRange'],
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
                nodeData: [],
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
                nodeColumns: [
                    {
                        prop: 'templateId',
                        label: i18n.templateId,
                        sortable: 'custom',
                        align: 'center'
                    },
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
                        prop: 'creator',
                        label: i18n.creator,
                        align: 'center'
                    },
                    {
                        prop: 'createTime',
                        label: i18n.createTime,
                        align: 'center',
                        width: 220
                    },
                    {
                        prop: 'atomTotal',
                        label: i18n.atomTotal,
                        sortable: 'custom',
                        align: 'center',
                        width: 120
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
                        prop: 'instanceTotal',
                        label: i18n.instanceTotal,
                        align: 'center',
                        sortable: 'custom',
                        width: 120
                    },
                    {
                        prop: 'relationshipTotal',
                        label: i18n.relationshipTotal,
                        align: 'center',
                        sortable: 'custom',
                        width: 160
                    },
                    {
                        prop: 'periodicTotal',
                        label: i18n.periodicTotal,
                        align: 'center',
                        sortable: 'custom',
                        width: 150
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
                selectedCcId: '',
                businessSelected: '',
                categorySelected: '',
                selectedCategory: '',
                choiceBusiness: '',
                choiceCategory: undefined
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
                return list
            },
            categoryList () {
                if (this.categorys.length === 0) {
                    this.getCategorys()
                }
                const list = tools.deepClone(this.categorys)
                return list
            }
        },
        watch: {
            timeRange: function (val) {
                this.onTemplateCategory(null)
                this.onTemplateBizCcId(null)
                this.onTemplateNode(val)
            }
        },
        created () {
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
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'category',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        biz_cc_id: this.choiceBusiness
                    })
                }
                this.templateData(data)
            },
            onClearTemplateCategory () {
                this.onTemplateCategory()
            },
            onTemplateNode (value) {
                if (this.tabName !== 'processDetails') {
                    // 防止不同界面进行触发接口调用
                    return
                }
                if (Array.isArray(value)) {
                    this.resetPageIndex()
                }
                this.isDetailLoading = true
                const time = this.getUTCTime(this.timeRange)
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
                const time = this.getUTCTime(this.timeRange)
                const data = {
                    group_by: 'biz_cc_id',
                    conditions: JSON.stringify({
                        create_time: time[0],
                        finish_time: time[1],
                        category: this.choiceCategory
                    })
                }
                this.templateBizIdData(data)
            },
            onClearTemplateBizCcId () {
                this.onTemplateBizCcId()
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
                }
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
                this.onTemplateNode()
            },
            onInstanceHandleView (index, row) {
                window.open(this.site_url + 'taskflow/home/' + row.businessId + '/?template_id=' + row.templateId)
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
.content-business-picker {
    vertical-align: top;
}

</style>
