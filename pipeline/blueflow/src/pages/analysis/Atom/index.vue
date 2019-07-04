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
        <bk-tab :active-name="'cite'" @tab-changed="changeTabPanel">
            <!-- 引用次数选项卡 -->
            <bk-tabpanel name="cite" :title="i18n.cite">
                <div class="p20">{{i18n.citeName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime1}}
                                    <el-date-picker :clearable="false" v-model="time" @change="plotlyDataByCite()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->
                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.businessName}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="plotlyDataByCite()" value="" v-model="biz_cc_id">
                                        <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->

                            </el-col>
                        </div>
                        <!-- plotly图表 -->
                        <el-col :span="20" :offset="1">
                            <div class="block analysis-plotly-class" id="citeBar" v-if="citeShow"></div>
                            <NoData class="empty-data" :style="{height: noDataHeight}" v-else/>
                        </el-col>
                        <!-- plotly图表end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 引用次数选项卡end -->

            <!-- 流程引用 -->
            <bk-tabpanel name="template" :title="i18n.template">
                <div class="p20">{{i18n.templateName}}</div>
                <el-col :span="24">
                <div class="grid-content bg-purple-dark">
                    <div class="block">
                        <el-col :span="20" :offset="3">

                            <!-- 原子选择器 -->
                            <el-col :span="5" class="analysis-select" :offset="0">
                                {{i18n.atom}}
                                <el-select filterable :placeholder="i18n.choice" @change="dataTableDataByTemplate()" value="" v-model="atom">
                                    <el-option v-for="item in components" :key="item.code"  :label="item.group_name +'-'+ item.name" :value="item.code">
                                    </el-option>
                                </el-select>
                            </el-col>
                            <!-- 原子选择器end -->

                            <!-- 时间选择器 -->
                            <el-col :span="8" class="analysis-date-picker" :offset="0">
                                {{i18n.startAndEndTime1}}
                                <el-date-picker :clearable="false" v-model="time" @change="dataTableDataByTemplate()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                </el-date-picker>
                            </el-col>
                            <!-- 时间选择器end -->

                            <!-- 业务选择器 -->
                            <el-col :span="5" class="analysis-select" :offset="0">
                                {{i18n.businessName}}
                                <el-select filterable :placeholder="i18n.choice" @change="dataTableDataByTemplate()" value="" v-model="biz_cc_id">
                                    <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                    </el-option>
                                </el-select>
                            </el-col>
                            <!-- 业务选择器end -->

                            <!-- 类型选择器 -->
                            <el-col :span="5" class="analysis-select" :offset="0">
                                {{i18n.category}}
                                <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByTemplate()" value="" v-model="category">
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
                        :data="templateData"
                        :total="templateTotal"
                        :otherHeight="otherHeight"
                        :pagination="templatePagination"
                        :options="templateOptions"
                        :columns="templateColumns"
                        :operates="templateOperates"
                        @handleSizeChange="templateHandleSizeChange"
                        @handleIndexChange="templateHandleIndexChange"
                        @handleFilter="handleFilter">
                        </data-table-pagination>
                    </el-col>
                    <!-- 表格end -->
                </div>
                </el-col>
            </bk-tabpanel>
            <!-- 流程引用选项卡 end -->

            <!-- 执行选项卡 -->
            <bk-tabpanel name="execute" :title="i18n.execute">
                <div class="p20">{{i18n.executeName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime3}}
                                    <el-date-picker :clearable="false" v-model="time" @change="dataTableDataByExecute()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.businessName}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByExecute()" value="" v-model="biz_cc_id">
                                        <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->

                                <!-- 类型选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.category}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByExecute()" value="" v-model="category">
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
                            :data="executeData"
                            :total="executeTotal"
                            :otherHeight="otherHeight"
                            :pagination="executePagination"
                            :options="executeOptions"
                            :columns="executeColumns"
                            :operates="executeOperates"
                            @handleSizeChange="executeHandleSizeChange"
                            @handleIndexChange="executeHandleIndexChange"
                            @handleFilter="handleFilter">
                            </data-table-pagination>
                        </el-col>
                        <!-- 表格end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 执行选项卡end -->

            <!-- 任务引用选项卡 -->
            <bk-tabpanel name="instance" :title="i18n.instance">
                <div class="p20">{{i18n.instanceName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 原子选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.atom}}
                                    <el-select filterable :placeholder="i18n.choice" @change="dataTableDataByInstance()" value="" v-model="atom">
                                        <el-option v-for="item in components" :key="item.code"  :label="item.group_name +'-'+ item.name" :value="item.code">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 原子选择器end -->

                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime3}}
                                    <el-date-picker :clearable="false" v-model="time" @change="dataTableDataByInstance()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.businessName}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByInstance()" value="" v-model="biz_cc_id">
                                        <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->

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
                            @handleFilter="handleFilter">
                            </data-table-pagination>
                        </el-col>
                        <!-- 表格end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 任务引用选项卡 end -->

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
    name: 'AnalysisAtom',
    components: {
        NoData,
        DataTablePagination
    },
    data () {
        return {
            i18n: {
                startAndEndTime1: gettext('流程创建时间：'),
                startAndEndTime2: gettext('原子执行时间：'),
                startAndEndTime3: gettext('任务开始时间：'),
                startTime: gettext('开始日期'),
                endTime: gettext('结束日期'),
                choice: gettext('请选择'),
                category: gettext('分类：'),
                businessName: gettext('业务：'),
                cite: gettext('引用次数'),
                citeName: gettext('各原子被流程模板直接引用次数'),
                atom: gettext('原子：'),
                template: gettext('流程详情'),
                templateName: gettext('引用原子的流程模板列表'),
                instance: gettext('任务详情'),
                instanceName: gettext('执行原子的任务列表'),
                execute: gettext('执行耗时'),
                executeName: gettext('各原子执行统计数据')
            },
            appType: 'app',
            time: [0, 0],
            category: '',
            biz_cc_id: '',
            atom: '',
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
            templateData: [], // 模板数据
            otherHeight: 208, // 除了table表格之外的高度，为了做table表格的高度自适应
            templateTotal: 0, // table数据总条数,
            templatePageIndex: 1, // 当前页码
            templateLimit: 15, // 每页数量
            templatePagination: {
                // 分页操作
                limit: this.templateLimit,
                pageIndex: this.templatePageIndex,
                pageArray: [15, 25]
            },
            templateOptions: {
                stripe: true, // 是否为斑马纹 table
                loading: false, // 是否添加表格loading加载动画
                highlightCurrentRow: true, // 是否支持当前行高亮显示
                mutiSelect: false, // 是否支持列表项选中功能
                filter: false, // 是否支持数据过滤功能
                action: true, // 是否支持表格操作功能
                border: true // 是否支持外边框
            },
            templateColumns: [
                {
                    prop: 'businessName', // 识别id
                    label: gettext('所属业务'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'templateName', // 识别id
                    label: gettext('流程名称'), // 表头显示名称
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
                }
            ],
            templateOperates: {
                // width: 200,
                // fixed: 'right',
                isShow: true, // 是否显示操作按钮
                flex: '0 0 100%',
                data: [
                    {
                        label: gettext('查看'), // 按钮显示文字
                        show: true, // 是否展示该按钮
                        cls: 'bk-button bk-primary btn-size-mini',
                        method: (index, row) => {
                            // 回调方法
                            this.templateHandleEdit(index, row)
                        }
                    }
                ]
            },
            executeData: [], // 执行数据
            executeTotal: 0, // table数据总条数,
            executePageIndex: 1, // 当前页码
            executeLimit: 15, // 每页数量
            executePagination: {
                // 分页操作
                limit: this.executeLimit,
                pageIndex: this.executePageIndex,
                pageArray: [15, 25]
            },
            executeOptions: {
                stripe: true, // 是否为斑马纹 table
                loading: false, // 是否添加表格loading加载动画
                highlightCurrentRow: true, // 是否支持当前行高亮显示
                mutiSelect: false, // 是否支持列表项选中功能
                filter: false, // 是否支持数据过滤功能
                action: true, // 是否支持表格操作功能
                border: true // 是否支持外边框
            },
            executeColumns: [
                {
                    prop: 'componentName',
                    label: gettext('原子名称'),
                    align: 'center'
                },
                {
                    prop: 'executeTimes', // 识别id
                    label: gettext('执行次数'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'failedTimes', // 识别id
                    label: gettext('失败次数'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'avgExecuteTime',
                    label: gettext('平均执行耗时（秒）'),
                    align: 'center'
                },
                {
                    prop: 'failedTimesPercent',
                    label: gettext('失败率'),
                    align: 'center'
                }
            ],
            executeOperates: {
                // width: 200,
                // fixed: 'right',
                flex: '0 0 100%',
                isShow: false, // 是否显示操作按钮
                data: [
                    {
                        label: gettext('查看'), // 按钮显示文字
                        type: 'primary', // 按钮类型 “primary / success / warning / danger / info / text”
                        show: true, // 是否展示该按钮
                        icon: 'el-icon-search', // 图标
                        plain: true, // 是否为朴素按钮
                        method: (index, row) => {
                            // 回调方法
                            this.handleEdit(index, row)
                        }
                    }
                ]
            },
            instanceData: [], // 模板数据
            instanceTotal: 0, // table数据总条数,
            instancePageIndex: 1, // 当前页码
            instanceLimit: 15, // 每页数量
            instancePagination: {
                // 分页操作
                limit: this.instanceLimit,
                pageIndex: this.instancePageIndex,
                pageArray: [15, 25]
            },
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
                    prop: 'businessName',
                    label: gettext('所属业务'),
                    align: 'center'
                },
                {
                    prop: 'instanceName', // 识别id
                    label: gettext('任务名称'), // 表头显示名称
                    align: 'center', // 对其格式，可选（right，left，center）
                    width: 300 // 宽度可选，默认自适应
                },
                {
                    prop: 'createTime',
                    label: gettext('创建时间'),
                    align: 'center',
                    width: 300
                },
                {
                    prop: 'creator',
                    label: gettext('创建人'),
                    align: 'center'
                },
                {
                    prop: 'category',
                    label: gettext('所属类型'),
                    align: 'center'
                }
            ],
            instanceOperates: {
                // width: 200,
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
                            this.instanceHandleSearch(index, row)
                        }
                    }
                ]
            },
            components: [],
            citeShow: true,
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
        this.plotlyDataByCite()
        if (this.categorys.length === 0) {
            this.getCategorys()
        }
        if (this.bizList.length === 0) {
            this.getBizList()
        }
        if (this.components.length === 0) {
            this.getComponentList()
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
        ...mapActions('atomList/', [
            'queryAtomData',
            'loadSingleAtomList'
        ]),
        ...mapActions([
            'getBizList',
            'getCategorys'
        ]),
        // 切换每页显示的数量
        templateHandleSizeChange (limit) {
            this.templatePageIndex = 1
            this.templateLimit = limit
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByTemplate()
        },
        // 切换页码
        templateHandleIndexChange (pageIndex) {
            this.templatePageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByTemplate()
        },
        // 切换每页显示的数量
        executeHandleSizeChange (limit) {
            this.executePageIndex = 1
            this.executeLimit = limit
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByExecute()
        },
        // 切换页码
        executeHandleIndexChange (pageIndex) {
            this.executePageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByExecute()
        },
        // 切换每页显示的数量
        instanceHandleSizeChange (limit) {
            this.instancePageIndex = 1
            this.instanceLimit = limit
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByInstance()
        },
        // 切换页码
        instanceHandleIndexChange (pageIndex) {
            this.instancePageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByInstance()
        },
        // 选中行
        handleSelectionChange (val) {
        },
        // 编辑
        templateHandleEdit (index, row) {
            window.open(this.site_url + 'template/edit/' + row.businessId + '/?template_id=' + row.templateId)
        },
        instanceHandleSearch (index, row) {
            window.open(this.site_url + 'taskflow/execute/' + row.businessId + '/?instance_id=' + row.instanceId)
        },
        handleFilter (value, row, column) {
            return row.code === value
        },
        handelAction () {
        },
        changeTabPanel (name) {
            switch (name) {
                case 'cite' :
                    this.plotlyDataByCite()
                    break
                case 'template' :
                    this.dataTableDataByTemplate()
                    break
                case 'execute' :
                    this.dataTableDataByExecute()
                    break
                case 'instance' :
                    this.dataTableDataByInstance()
                    break
            }
        },
        async queryPlotlyData (data, id, title) {
            const templateData = await this.queryAtomData(data)
            let total = templateData.data.total
            if (id === 'citeBar' && total === 0) {
                this.citeShow = false
                return
            }
            else if (id === 'citeBar') {
                this.citeShow = true
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
        plotlyDataByCite () {
            const data = {
                group_by: 'atom_cite',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    biz_cc_id: this.biz_cc_id,
                    finish_time: this.time[1]
                })
            }
            this.queryPlotlyData(data, 'citeBar', gettext('原子被引用次数'))
        },
        async queryDataTableData (data) {
            const templateData = await this.queryAtomData(data)
            switch (data.group_by) {
                case 'atom_template':
                    this.templateData = templateData.data.groups
                    this.templateTotal = templateData.data.total
                    break
                case 'atom_execute':
                    this.executeData = templateData.data.groups
                    this.executeTotal = templateData.data.total
                    break
                case 'atom_instance':
                    this.instanceData = templateData.data.groups
                    this.instanceTotal = templateData.data.total
                    break
            }
        },
        dataTableDataByTemplate () {
            const data = {
                group_by: 'atom_template',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    biz_cc_id: this.biz_cc_id,
                    category: this.category,
                    component_code: this.atom
                }),
                pageIndex: this.templatePageIndex,
                limit: this.templateLimit
            }
            this.queryDataTableData(data)
        },
        dataTableDataByExecute () {
            const data = {
                group_by: 'atom_execute',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    biz_cc_id: this.biz_cc_id,
                    category: this.category
                }),
                pageIndex: this.executePageIndex,
                limit: this.executeLimit
            }
            this.queryDataTableData(data)
        },
        dataTableDataByInstance () {
            const data = {
                group_by: 'atom_instance',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    biz_cc_id: this.biz_cc_id,
                    category: this.category,
                    component_code: this.atom
                }),
                pageIndex: this.instancePageIndex,
                limit: this.instanceLimit
            }
            this.queryDataTableData(data)
        },
        async getComponentList () {
            this.components = await this.loadSingleAtomList()
            this.atom = this.components[0].code
        }
    }
}
</script>

