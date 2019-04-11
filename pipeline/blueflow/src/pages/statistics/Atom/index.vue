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
            <div class="content-dimesion atom-statistics" v-bkloading="{isLoading: isCitationLoading, opacity: 1}">
                <div class="clearfix">
                    <div class="content-title">{{i18n.numberCitations}}</div>
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
                                @item-selected="onAtomCiteData">
                            </bk-selector>
                        </div>
                        <div class="content-date-picker" @click="onDatePickerClick">
                            <bk-date-range
                                ref="datePickerRef"
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
                <data-statistics :dimensionList="taskPlotData" :totalValue="taskTotal"></data-statistics>
            </div>
        </div>
        <div class="content-process-detail">
            <bk-tab :type="'fill'" :active-name="tabName" @tab-changed="onChangeTabPanel">
                <bk-tabpanel name="processDetails" :title="i18n.processDetail">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.atom}}</label>
                                <bk-selector
                                    :list="componentsList"
                                    :display-key="'name'"
                                    :setting-name="'code'"
                                    :search-key="'name'"
                                    :setting-key="'code'"
                                    :selected.sync="selectedAtom"
                                    :placeholder="i18n.choice"
                                    :searchable="true"
                                    :allow-clear="true"
                                    @change="onAtomTemplateData"
                                    @clear="onClearAtom"
                                    @item-selected="onSelectedAtom">
                                </bk-selector>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.taskStartTime}}</label>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onAtomTemplateData">
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
                                    @change="onAtomTemplateData"
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
                                    @change="onAtomTemplateData"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="templateData"
                            :total="templateTotal"
                            :options="dataTableOptions"
                            :pagination="templatePagination"
                            :columns="templateColumns"
                            :loading="isTemplateLoading"
                            @handleSizeChange="onTemplateHandleSizeChange"
                            @handleIndexChange="onTemplateHandleIndexChange">
                        </data-table-pagination>
                    </div>
                </bk-tabpanel>
                <bk-tabpanel name="executionTime" :title="i18n.executionTime">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.taskStartTime}}</label>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onAtomExecuteData">
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
                                    @change="onAtomExecuteData"
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
                                    @change="onAtomExecuteData"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="executeData"
                            :total="executeTotal"
                            :columns="executeColumns"
                            :pagination="executePagination"
                            :loading="isExecutionLoading"
                            @handleSizeChange="onExecuteHandleSizeChange"
                            @handleIndexChange="onExecuteHandleIndexChange">
                        </data-table-pagination>
                    </div>
                </bk-tabpanel>
                <bk-tabpanel name="taskDetails" :title="i18n.taskDetail">
                    <div class="content-wrap-detail">
                        <div class="content-wrap-from">
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.atom}}</label>
                                <bk-selector
                                    :list="componentsList"
                                    :display-key="'name'"
                                    :setting-name="'code'"
                                    :search-key="'name'"
                                    :setting-key="'code'"
                                    :selected.sync="selectedAtom"
                                    :placeholder="i18n.choice"
                                    :searchable="true"
                                    :allow-clear="true"
                                    @change="onAtomTemplateData"
                                    @clear="onClearAtom"
                                    @item-selected="onSelectedAtom">
                                </bk-selector>
                            </div>
                            <div class="content-wrap-select">
                                <label class="content-detail-label">{{i18n.taskStartTime}}</label>
                                <bk-date-range
                                    :quick-select="true"
                                    :start-date="tableStartTime"
                                    :end-date="tableEndTime"
                                    :end-date-max="endDateMax"
                                    @change="onAtomInstanceData">
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
                                    @change="onAtomInstanceData"
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
                                    @change="onAtomInstanceData"
                                    @clear="onClearCategory"
                                    @item-selected="onSelectedCategory">
                                </bk-selector>
                            </div>
                        </div>
                        <data-table-pagination
                            :data="instanceData"
                            :total="instanceTotal"
                            :options="dataTableOptions"
                            :pagination="instancePagination"
                            :columns="instanceColumns"
                            :loading="isInstanceLoading"
                            @handleSizeChange="onInstanceHandleSizeChange"
                            @handleIndexChange="onInstanceHandleIndexChange">
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
    numberCitations: gettext('引用次数'),
    processDetail: gettext('流程详情'),
    executionTime: gettext('执行耗时'),
    taskDetail: gettext('任务详情'),
    timeLimit: gettext('时间范围'),
    taskStartTime: gettext('任务开始时间'),
    choiceCategory: gettext('选择分类'),
    choiceBusiness: gettext('选择业务'),
    choice: gettext('请选择'),
    atom: gettext('标准插件'),
    choiceAllCategory: gettext('全部分类'),
    choiceAllBusiness: gettext('全部业务'),
    templateName: gettext('流程名称'),
    businessName: gettext('所属业务'),
    editTime: gettext('更新时间'),
    editor: gettext('更新人'),
    category: gettext('分类'),
    instanceName: gettext('任务名称'),
    createTime: gettext('创建时间'),
    creator: gettext('创建人'),
    atomTotal: gettext('标准插件数'),
    subprocessTotal: gettext('子流程数'),
    gatewaysTotal: gettext('网关数'),
    componentName: gettext('标准插件'),
    executeTimes: gettext('执行次数'),
    failedTimes: gettext('失败次数'),
    avgExecuteTime: gettext('平均执行耗时(秒)'),
    failedTimesPercent: gettext('失败率')
}

export default {
    name: 'StatisticsAtom',
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
            isDropdownShow: false,
            choiceDownShow: false,
            datePickerRefShow: false,
            isTemplateLoading: true,
            isCitationLoading: true,
            isExecutionLoading: true,
            isInstanceLoading: true,
            time: [0, 0],
            taskPlotData: [],
            nodeData: [],
            templateData: [],
            templateTotal: 0,
            templatePageIndex: 1,
            templateLimit: 15,
            templatePagination: {
                limit: this.templateLimit,
                pageIndex: this.templatePageIndex,
                pageArray: this.dataTablePageArray
            },
            templateColumns: [
                {
                    prop: 'templateName', // 识别id
                    label: i18n.templateName,// 表头显示名称
                    width: '285',
                    title: 'templateName',
                    formatter: (row, column, cellValue, index) => {
                        return `<a class="template-router" target="_blank" href="${this.site_url}template/edit/${row.businessId}/?template_id=${row.templateId}">${row.templateName}</a>`
                    }
                },
                {
                    prop: 'businessName', // 识别id
                    label: i18n.businessName, // 表头显示名称
                    align: 'center'// 对其格式，可选（right，left，center）
                },
                {
                    prop: 'editTime',
                    label: i18n.editTime,
                    align: 'center'
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
                }
            ],
            tabName: 'processDetails',
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
                    label: i18n.businessName, // 表头显示名称
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
                    align: 'center'
                },
                {
                    prop: 'subprocessTotal',
                    label: i18n.subprocessTotal,
                    align: 'center'
                },
                {
                    prop: 'gatewaysTotal',
                    label: i18n.gatewaysTotal,
                    align: 'center'
                }
            ],
            atom: '',
            components: [],
            executeData: [],
            executeTotal: 0,
            executePageIndex: 1,
            executeLimit: 15,
            executePagination: {
                limit: this.executeLimit,
                pageIndex: this.executePageIndex,
                pageArray: this.dataTablePageArray
            },
            executeColumns: [
                {
                    prop: 'componentName',
                    label: i18n.componentName
                },
                {
                    prop: 'executeTimes',
                    label: i18n.executeTimes,
                    align: 'center'
                },
                {
                    prop: 'failedTimes',
                    label: i18n.failedTimes,
                    align: 'center'
                },
                {
                    prop: 'avgExecuteTime',
                    label: i18n.avgExecuteTime,
                    align: 'center'
                },
                {
                    prop: 'failedTimesPercent',
                    label: i18n.failedTimesPercent,
                    align: 'center'
                }
            ],
            instanceData: [],
            instanceTotal: 0,
            taskTotal: 0,
            instancePageIndex: 1,
            instanceLimit: 15,
            instancePagination: {
                limit: this.instanceLimit,
                pageIndex: this.instancePageIndex,
                pageArray: this.dataTablePageArray
            },
            instanceColumns: [
                {
                    prop: 'instanceName',
                    label: i18n.instanceName,
                    formatter: (row, column, cellValue, index) => {
                        return `<a class="template-router" target="_blank" href="${this.site_url}taskflow/execute/${row.businessId}/?instance_id=${row.instanceId}">${row.instanceName}</a>`
                    }
                },
                {
                    prop: 'businessName',
                    label: i18n.businessName,
                    align: 'center'
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
                }
            ],
            selectedCcId: -1,
            selectedCategory: -1,
            selectedAtom: -1,
            choiceBusiness: undefined,
            tableStartTime: undefined,
            tableEndTime: undefined,
            businessStartTime: undefined,
            businessEndTime: undefined,
            endDateMax: '',
            businessSelected: 'all'
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
        componentsList () {
            // 选择器组件不支持拼接的字段，需要转换
            if (this.components) {
                return this.components.map((item) => {
                    item.name = item.group_name + '-' + item.name
                    return item
                })
            }
            return []
        }
    },
    created () {
        this.getDateTime()
        this.choiceBusinessName = this.i18n.choiceAllBusiness
    },
    mounted () {
        if (this.components.length === 0) {
            this.getComponentList()
        }
    },
    methods: {
        ...mapActions('atomList/', [
            'queryAtomData',
            'loadSingleAtomList'
        ]),
        ...mapActions([
            'getBizList',
            'getCategorys'
        ]),
        onTemplateHandleSizeChange (limit) {
            this.templatePageIndex = 1
            this.templateLimit = limit
            this.onAtomTemplateData()
        },
        onTemplateHandleIndexChange (pageIndex) {
            this.templatePageIndex = pageIndex
            this.onAtomTemplateData()
        },
        onExecuteHandleSizeChange (limit) {
            this.executePageIndex = 1
            this.executeLimit = limit
            this.onAtomExecuteData()
        },
        onExecuteHandleIndexChange (pageIndex) {
            this.executePageIndex = pageIndex
            this.onAtomExecuteData()
        },
        onInstanceHandleSizeChange (limit) {
            this.instancePageIndex = 1
            this.instanceLimit = limit
            this.onAtomInstanceData()
        },
        onInstanceHandleIndexChange (pageIndex) {
            this.instancePageIndex = pageIndex
            this.onAtomInstanceData()
        },
        onAtomCiteData (business, name) {
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
            const time = this.getUTCTime([this.businessStartTime, this.businessEndTime])
            const data = {
                group_by: 'atom_cite',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.choiceBusiness === 'all' ? '' : this.choiceBusiness
                })
            }
            this.atomData(data)
        },
        onAtomTemplateData (oldValue = null, newValue = null) {
            if (this.tabName !== 'processDetails' || this.atom === '') {
                // 防止不同界面进行触发接口调用
                // 防止标准插件数据未获取就发送数据
                return
            }
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            this.isTemplateLoading = true
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
            const data = {
                group_by: 'atom_template',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.bizCcId,
                    category: this.category,
                    component_code: this.atom
                }),
                pageIndex: this.templatePageIndex,
                limit: this.templateLimit
            }
            try {
                this.atomTableData(data)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onAtomExecuteData (oldValue = null, newValue = null) {
            if (this.tabName !== 'executionTime') {
                // 防止不同界面进行触发接口调用
                return
            }
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            this.isExecutionLoading = true
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
            const data = {
                group_by: 'atom_execute',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.bizCcId,
                    category: this.category
                }),
                pageIndex: this.executePageIndex,
                limit: this.executeLimit
            }
            try {
                this.atomTableData(data)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async atomTableData (data) {
            try {
                const templateData = await this.queryAtomData(data)
                switch (data.group_by) {
                    case 'atom_template':
                        this.templateData = templateData.data.groups
                        this.templateTotal = templateData.data.total
                        this.isTemplateLoading = false
                        break
                    case 'atom_execute':
                        this.executeData = templateData.data.groups
                        this.executeTotal = templateData.data.total
                        this.isExecutionLoading = false
                        break
                    case 'atom_instance':
                        this.instanceData = templateData.data.groups
                        this.instanceTotal = templateData.data.total
                        this.isInstanceLoading = false
                        break
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async atomData (data) {
            this.isCitationLoading = true
            try  {
                const templateData = await this.queryAtomData(data)
                this.taskPlotData = templateData.data.groups
                this.taskTotal = templateData.data.total
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.isCitationLoading = false
            }
        },
        onAtomInstanceData (oldValue = null, newValue = null) {
            if (this.tabName !== 'taskDetails') {
                // 防止不同界面进行触发接口调用
                return
            }
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.tableStartTime = dateArray[0]
                this.tableEndTime = dateArray[1]
                this.resetPageIndex()
            }
            this.isInstanceLoading = true
            const time = this.getUTCTime([this.tableStartTime, this.tableEndTime])
            const data = {
                group_by: 'atom_instance',
                conditions: JSON.stringify({
                    create_time: time[0],
                    finish_time: time[1],
                    biz_cc_id: this.bizCcId,
                    category: this.category,
                    component_code: this.atom
                }),
                pageIndex: this.instancePageIndex,
                limit: this.instanceLimit
            }
            try {
                this.atomTableData(data)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async getComponentList () {
            try {
                this.components = await this.loadSingleAtomList()
                this.atom = this.components[0].code
                this.selectedAtom = this.atom
                this.onAtomTemplateData(null)
            } catch (e) {
                errorHandler(e, this)
            }
        },
        getDateTime () {
            const date = new Date()
            date.setHours(0, 0, 0)
            const endTime = moment(date).format('YYYY-MM-DD')
            this.tableEndTime = endTime
            this.businessEndTime = endTime
            this.endDateMax = endTime
            date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
            const startTime = moment(date).format('YYYY-MM-DD')
            this.tableStartTime = startTime
            this.businessStartTime = startTime
        },
        onChangeTabPanel (name) {
            this.tabName = name
            switch (name) {
                case 'processDetails' :
                    this.onAtomTemplateData()
                    break
                case 'executionTime' :
                    this.onAtomExecuteData()
                    break
                case 'taskDetails':
                    this.onAtomInstanceData()
                    break
            }
        },
        onDatePickerClick () {
            this.datePickerRefShow = !this.datePickerRefShow
            this.$refs.datePickerRef.pickerVisible = this.datePickerRefShow
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
        onSelectedAtom (name, value) {
            if (this.atom === name) {
                return
            }
            this.atom = name
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
        onClearAtom () {
            this.selectedAtom = -1
            this.atom = undefined
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        },
        onChangeBusinessTime (oldValue, newValue) {
            if (newValue) {
                const dateArray = newValue.split(' - ')
                this.businessStartTime = dateArray[0]
                this.businessEndTime = dateArray[1]
            }
            this.onAtomCiteData(null)
        },
        resetPageIndex () {
            switch (this.tabName) {
                case 'processDetails':
                    this.templatePageIndex = 1
                    this.templatePagination.pageIndex = 1
                    break
                case 'exectionTime':
                    this.executePageIndex = 1
                    this.executePagination.pageIndex = 1
                    break
                case 'taskDetails':
                    this.instancePageIndex = 1
                    this.instancePagination.pageIndex = 1
            }
        }
    }
}
</script>

<style lang="scss">
.content-box {
    .content-wrap {
        .content-dimesion.atom-statistics {
            width: 100%;
            .chart-statistics-tool .tool-name {
                width: 250px;
            }
        }
    }
}
</style>
