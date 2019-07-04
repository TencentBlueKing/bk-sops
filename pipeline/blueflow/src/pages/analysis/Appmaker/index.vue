/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
<div id="app">
    <!-- 内容 -->
    <el-container direction="vertical">
        <!-- 选项卡 -->
        <bk-tab :active-name="'prop'" @tab-changed="changeTabPanel">
            <!-- 占比选项卡 -->
            <bk-tabpanel name="prop" :title="i18n.prop">
                <div class="p20">{{i18n.propName}}</div>
                <el-col :span="24">
                <div class="grid-content bg-purple-dark">
                    <div class="block">
                        <el-col :span="20" :offset="3">
                            <!-- 时间选择器 -->
                            <el-col :span="8" class="analysis-date-picker" :offset="0">
                                {{i18n.startAndEndTime}}
                                <el-date-picker :clearable="false" v-model="time" @change="plotlyDataByBizCCId()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                </el-date-picker>
                            </el-col>
                            <!-- 时间选择器end -->

                            <!-- 业务选择器 -->
                            <el-col :span="5" class="analysis-select" :offset="0" >
                                {{i18n.businessName}}
                                <el-select clearable filterable :placeholder="i18n.choice" @change="plotlyDataByBizCCId()" value="" v-model="biz_cc_id">
                                    <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                    </el-option>
                                </el-select>
                            </el-col>
                            <!-- 业务选择器end -->
                        </el-col>

                    </div>
                     <!-- plotly图表 -->
                    <el-col :span="20" :offset="1">
                        <div class="block analysis-plotly-class" id="propBar" v-if="propShow"></div>
                        <NoData class="empty-data" :style="{height: noDataHeight}" v-else/>
                    </el-col>
                    <!-- plotly图表end -->
                </div>
                </el-col>
            </bk-tabpanel>
            <!-- 占比选项卡end -->

            <!-- 轻应用选项卡 -->
            <bk-tabpanel name="appmaker" :title="i18n.appmaker">
                <div class="p20">{{i18n.appmakerName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime}}
                                    <el-date-picker :clearable="false" v-model="time" @change="plotlyDataByCategory()" type="daterange" align="right" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.category}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="plotlyDataByCategory()" value="" v-model="category">
                                        <el-option v-for="item in categorys" :key="item.value"  :label="item.name" :value="item.value">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->
                            </el-col>
                        </div>
                        <!-- plotly图表 -->
                        <el-col :span="20" :offset="1">
                            <div class="block analysis-plotly-class" id="appmakerBar" v-if="appmakerShow"></div>
                             <NoData class="empty-data" :style="{height: noDataHeight}" v-else/>
                        </el-col>
                        <!-- plotly图表end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 轻应用选项卡end -->

            <!-- 详情选项卡 -->
            <bk-tabpanel name="instance" :title="i18n.instance">
                <div class="p20">{{i18n.instanceName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime}}
                                    <el-date-picker :clearable="false" v-model="time" @change="dataTableDataByInstance()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 类型选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.category}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByInstance()" value="" v-model="category">
                                        <el-option v-for="item in categorys" :key="item.value"  :label="item.name" :value="item.value">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 类型选择器end -->
                            </el-col>
                        </div>
                        <!-- 表格 -->
                        <el-col :span="19" :offset="3" :style="{marginTop: '40px'}">
                            <data-table-pagination
                            :data="instanceData"
                            :total="instanceTotal"
                            :otherHeight="otherHeight"
                            :pagination="instancePagination"
                            :options="instanceOptions"
                            :columns="instanceColumns"
                            :operates="instanceOperates"
                            @handleSizeChange="instanceHandleSizeChange"
                            @handleIndexChange="instanceHandleIndexChange"
                            >
                            </data-table-pagination>
                        </el-col>
                        <!-- 表格end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!--  详情选项卡 end -->
        </bk-tab>
        <!-- 选项卡end -->
    </el-container>
    <!-- 内容end -->
</div>
</template>

<script>
import '@/utils/i18n.js'
import Plotly from 'plotly.js/dist/plotly-basic'
import Vue from 'vue'
import axios from 'axios'
import {mapActions, mapState} from 'vuex'
import DataTablePagination from '@/components/common/dataTable/DataTablePagination.vue'
import NoData from '@/components/common/base/NoData.vue'

export default {
    name: 'AnalysisAppmaker',
    components: {
        NoData,
        DataTablePagination
    },
    data () {
        return {
            i18n: {
                startAndEndTime: gettext('轻应用创建时间：'),
                startTime: gettext('开始日期'),
                endTime: gettext('结束日期'),
                choice: gettext('请选择'),
                category: gettext('分类：'),
                businessName: gettext('业务：'),
                appmaker: gettext('所属业务'),
                appmakerName: gettext('各业务中轻应用个数和占比'),
                prop: gettext('轻应用分类'),
                propName: gettext('各类型轻应用个数和占比'),
                instance: gettext('轻应用详情'),
                instanceName: gettext('各轻应用详情和创建任务个数')
            },
            appType: 'app',
            category: '',
            biz_cc_id: '',
            instanceData: [],
            time: [0, 0],
            pickerOptions1: {
                disabledDate (time) {
                    return time.getTime() > Date.now()
                },
                shortcuts: [
                    // 日期选择器 选择时间
                    {
                        text: gettext('今天'),
                        onClick (picker) {
                            picker.$emit('pick', [new Date(), new Date()])
                        }
                    },
                    {
                        text: gettext('昨天'),
                        onClick (picker) {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24)
                            picker.$emit('pick', [start, end])
                        }
                    },
                    {
                        text: gettext('一周前'),
                        onClick (picker) {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                            picker.$emit('pick', [start, end])
                        }
                    },
                    {
                        text: gettext('一月前'),
                        onClick (picker) {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                            picker.$emit('pick', [start, end])
                        }
                    },
                    {
                        text: gettext('三月前'),
                        onClick (picker) {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30 * 3)
                            picker.$emit('pick', [start, end])
                        }
                    }
                ]
            },
            otherHeight: 208, // 除了table表格之外的高度，为了做table表格的高度自适应
            instanceTotal: 0, // table数据总条数,
            instancePageIndex: 1, // 当前页码
            instanceLimit: 15, // 每页数量
            instancePagination: {
                limit: this.instanceLimit,
                pageIndex: this.instancePageIndex,
                pageArray: [15, 25]
            }, // 分页操作
            instanceOptions: {
                stripe: true, // 是否为斑马纹 table
                loading: false, // 是否添加表格loading加载动画
                highlightCurrentRow: true, // 是否支持当前行高亮显示
                mutiSelect: false, // 是否支持列表项选中功能
                filter: false, // 是否支持数据过滤功能
                action: true, // 是否支持表格操作功能
                border: true // 是否支持外边框
            },
            instanceColumns: [
                {
                    prop: 'businessName', // 识别id
                    label: gettext('所属业务'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'templateName', // 识别id
                    label: gettext('轻应用名称'), // 表头显示名称
                    align: 'center', // 对其格式，可选（right，left，center）
                    // sortable: true // 是否开启排序功能，默认为false
                    width: 300 // 宽度可选，默认自适应
                },
                {
                    prop: 'editTime',
                    label: gettext('更新时间'),
                    align: 'center',
                    width: 300
                },
                {
                    prop: 'editor', // 识别id
                    label: gettext('更新人'), // 表头显示名称
                    align: 'center', // 对其格式，可选（right，left，center）
                    formatter: (row, column, cellValue) => {
                        // 进行内容格式化
                        if (row.editor === '' || row.editor === null) {
                            return `<span>--</span>`
                        }
                        return `<span>${row.editor}</span>`
                    }
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'category', // 识别id
                    label: gettext('分类'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'instanceTotal', // 识别id
                    label: gettext('创建任务个数'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                }
            ],
            instanceOperates: {
                // width: 400,
                // fixed: 'right',
                flex: '0 0 100%',
                isShow: true, // 是否显示操作按钮
                data: [
                    {
                        label: gettext('查看'), // 按钮显示文字
                        show: true, // 是否展示该按钮
                        cls: 'bk-button bk-primary btn-size-mini',
                        method: (index, row) => {
                            // 回调方法
                            this.handleEdit(index, row)
                        }
                    }
                ]
            },
            appmakerShow: true,
            propShow: true,
            noDataHeight: '600px'
        }
    },
    created () {
        // 设置默认为30天前的查询
        let date = new Date()
        this.time[1] = Date.parse(date)
        date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
        this.time[0] = Date.parse(date)
    },
    mounted () {
        this.plotlyDataByBizCCId()
        if (this.categorys.length === 0) {
            this.getCategorys()
        }
        if (this.bizList.length === 0) {
            this.getBizList()
        }
    },
    computed: {
        ...mapState({
            bizList: state => state.bizList,
            categorys: state => state.categorys,
            site_url: state => state.site_url
        })
    },
    methods: {
        ...mapActions('appmaker/', [
            'queryAppmakerData'
        ]),
        ...mapActions([
            'getBizList',
            'getCategorys'
        ]),
        // 切换每页显示的数量
        handleSizeChange (limit) {
            this.limit = limit
            // 根据 pageSize 和 limit 进行请求发送
        },
        // 切换页码
        handleIndexChange (pageIndex) {
            this.pageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
        },
        // // 选中行
        handleSelectionChange (val) {
        },
        // 切换每页显示的数量
        instanceHandleSizeChange (limit) {
            this.instancePageIndex = 1
            this.instanceLimit = limit
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByinstance()
        },
        // 切换页码
        instanceHandleIndexChange (pageIndex) {
            this.instancePageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByinstance()
        },
        // 编辑
        handleEdit (index, row) {
            window.open(this.site_url + 'appmaker/home/' + row.businessId + '/')
        },
        changeTabPanel (name) {
            switch (name) {
                case 'appmaker' :
                    this.plotlyDataByCategory()
                    break
                case 'prop' :
                    this.plotlyDataByBizCCId()
                    break
                case 'instance' :
                    this.dataTableDataByInstance()
                    break
            }
        },
        async queryPlotlyData (data, id, title, seriesTitle) {
            const templateData = await this.queryAppmakerData(data)
            let total = templateData.data.total
            if (id === 'propBar' && total === 0) {
                this.propShow = false
                return
            }
            else if (id === 'propBar') {
                this.propShow = true
                this.$nextTick(function () {
                    this.createPolt(id, total, templateData.data.groups, title)
                })
            }
            else if (id === 'appmakerBar' && total === 0) {
                this.appmakerShow = false
                return
            }
            else if (id === 'appmakerBar') {
                this.appmakerShow = true
                this.$nextTick(function () {
                    this.createPolt(id, total, templateData.data.groups, title)
                })
            }
        },
        createPolt (id, total, tableData, title) {
            tableData.sort((val1, val2) => val1.value - val2.value)
            let groupData = []
            let valueData = []
            let propData = []
            let widthList = []
            let size = null
            let length = tableData.length
            if (length === 1) {
                size = 0.1
            }
            else if (length < 3) {
                size = 0.2
            }
            else if (length < 4) {
                size = 0.3
            }
            else if (length < 5) {
                size = 0.5
            }
            else if (length < 10) {
                size = 0.7
            }
            else if (length < 15) {
                size = 0.9
            }
            else {
                size = 0.7
            }
            for (let i = 0; i < tableData.length; i++) {
                groupData.push(tableData[i].name)
                let value = tableData[i].value
                valueData.push(value)
                let fixedVal = (100 * parseFloat(value) / parseFloat(total)).toFixed(2)
                if (isNaN(fixedVal)) {
                    fixedVal = 0
                }
                propData.push(gettext('数量:') + value + gettext(' 占比:') + fixedVal + '%')
                widthList.push(size)
            }
            const colors = ['#62d1de', '#54d6b6', '#a6db69', '#ffd454', '#ffa361', '#d1d1d1']
            const chartsData = [{
                x: valueData,
                y: groupData,
                type: 'bar',
                orientation: 'h',
                marker: colors,
                hoverinfo: 'text',
                hovertext: propData,
                opacity: 0.6,
                width: widthList
            }]
            const layout = {
                width: 1000,
                height: 600,
                title: title,
                xaxis: {
                    tickvals: valueData,
                    automargin: true
                },
                yaxis: {
                    automargin: true,
                    ticklen: 12
                }
            }
            Plotly.newPlot(id, chartsData, layout, {displayModeBar: false})
        },
        plotlyDataByCategory () {
            const data = {
                group_by: 'biz_cc_id',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    biz_cc_id: this.biz_cc_id,
                    finish_time: this.time[1]
                })
            }
            this.queryPlotlyData(data, 'appmakerBar', gettext('轻应用个数和占比'))
        },
        plotlyDataByBizCCId () {
            const data = {
                group_by: 'category',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    category: this.category
                })
            }
            this.queryPlotlyData(data, 'propBar', gettext('轻应用个数和占比'))
        },
        async queryDataTableData (data) {
            const templateData = await this.queryAppmakerData(data)
            switch (data.group_by) {
                case 'appmaker_instance':
                    this.instanceData = templateData.data.groups
                    this.instanceTotal = templateData.data.total
                    break
            }
        },
        dataTableDataByInstance () {
            const data = {
                group_by: 'appmaker_instance',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    biz_cc_id: this.biz_cc_id,
                    category: this.category
                }),
                pageIndex: this.citePageIndex,
                limit: this.citeLimit
            }
            this.queryDataTableData(data)
        }
    }
}
</script>
