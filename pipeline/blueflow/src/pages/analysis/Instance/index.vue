<template>
<div id="app">
    <!-- 内容 -->
    <el-container direction="vertical">
        <!-- 选项卡 -->
        <bk-tab :active-name="'instance'" @tab-changed="changeTabPanel">
            <!-- 实例选项卡 -->
            <bk-tabpanel name="instance" :title="i18n.instance">
                <div class="p20">{{i18n.instanceName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime}}
                                    <el-date-picker :clearable="false" v-model="time" @change="plotlyDataByCategory()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.businessName}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="plotlyDataByCategory()" value="" v-model="biz_cc_id">
                                        <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->
                            </el-col>
                        </div>
                        <!-- plotly图表 -->
                        <el-col :span="20" :offset="1">
                            <div class="block analysis-plotly-class" id="instanceBar" v-if="instanceShow"></div>
                            <NoData class="empty-data" :style="{height: noDataHeight}" v-else/>
                        </el-col>
                        <!-- plotly图表end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 实例选项卡end -->

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

                            <!-- 类型选择器 -->
                            <el-col :span="5" class="analysis-select" :offset="0">
                                {{i18n.category}}
                                <el-select clearable filterable :placeholder="i18n.choice" @change="plotlyDataByBizCCId()" value="" v-model="category">
                                    <el-option v-for="item in categorys" :key="item.value"  :label="item.name" :value="item.value">
                                    </el-option>
                                </el-select>
                            </el-col>
                            <!-- 类型选择器end -->
                        </el-col>
                    </div>
                     <!-- plotly图表 -->
                    <el-col :span="20" :offset="1">
                        <div class="block analysis-plotly-class" id="propBar" v-if="propShow" ></div>
                        <NoData class="empty-data" :style="{height: noDataHeight}" v-else/>
                    </el-col>
                    <!-- plotly图表end -->
                </div>
                </el-col>
            </bk-tabpanel>
            <!-- 占比选项卡end -->

            <!-- 详情选项卡 -->
            <bk-tabpanel name="node" :title="i18n.node">
                <div class="p20">{{i18n.nodeName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime}}
                                    <el-date-picker :clearable="false" v-model="time" @change="dataTableDataByNode()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.businessName}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByNode()" value="" v-model="biz_cc_id">
                                        <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->

                                <!-- 类型选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.category}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByNode()" value="" v-model="category">
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
                            :data="nodeData"
                            :total="nodeTotal"
                            :otherHeight="otherHeight"
                            :pagination="nodePagination"
                            :options="nodeOptions"
                            :columns="nodeColumns"
                            :operates="nodeOperates"
                            @handleSizeChange="nodeHandleSizeChange"
                            @handleIndexChange="nodeHandleIndexChange"
                            @handleSelectionChange="handleSelectionChange">
                            </data-table-pagination>
                        </el-col>
                        <!-- 表格end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 详情选项卡end -->

            <!-- 耗时选项卡 -->
            <bk-tabpanel name="details" :title="i18n.details">
                <div class="p20">{{i18n.detailsName}}</div>
                <el-col :span="24">
                    <div class="grid-content bg-purple-dark">
                        <div class="block">
                            <el-col :span="20" :offset="3">
                                <!-- 时间选择器 -->
                                <el-col :span="8" class="analysis-date-picker" :offset="0">
                                    {{i18n.startAndEndTime}}
                                    <el-date-picker :clearable="false" v-model="time" @change="dataTableDataByDetails()" align="right" type="daterange" format="yyyy-MM-dd" value-format="timestamp"  :start-placeholder="i18n.startTime" :end-placeholder="i18n.endTime" :picker-options="pickerOptions1">
                                    </el-date-picker>
                                </el-col>
                                <!-- 时间选择器end -->

                                <!-- 业务选择器 -->
                                <el-col :span="5" class="analysis-select" :offset="0">
                                    {{i18n.businessName}}
                                    <el-select clearable filterable :placeholder="i18n.choice" @change="dataTableDataByDetails()" value="" v-model="biz_cc_id">
                                        <el-option v-for="item in bizList" :key="item.cc_id"  :label="item.cc_name" :value="item.cc_id">
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <!-- 业务选择器end -->
                            </el-col>
                        </div>
                        <!-- 表格 -->
                        <el-col :span="19" :offset="3" :style="{marginTop: '40px'}">
                            <data-table-pagination
                            :data="detailsData"
                            :total="detailsTotal"
                            :otherHeight="otherHeight"
                            :pagination="detailsPagination"
                            :options="detailsOptions"
                            :columns="detailsColumns"
                            :operates="detailsOperates"
                            @handleSizeChange="detailsHandleSizeChange"
                            @handleIndexChange="detailsHandleIndexChange"
                            @handleSelectionChange="handleSelectionChange"
                            @handleFilter="handleFilter">
                            </data-table-pagination>
                        </el-col>
                        <!-- 表格end -->
                    </div>
                </el-col>
            </bk-tabpanel>
            <!-- 耗时选项卡end -->

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
    name: 'AnalysisInstance',
    components: {
        NoData,
        DataTablePagination
    },
    data () {
        return {
            i18n: {
                startAndEndTime: gettext('任务创建时间：'),
                startTime: gettext('开始日期'),
                endTime: gettext('结束日期'),
                choice: gettext('请选择'),
                category: gettext('分类：'),
                businessName: gettext('业务：'),
                instanceName: gettext('任务分类统计数据'),
                propName: gettext('任务按业务维度统计数据'),
                node: gettext('任务详情'),
                details: gettext('执行耗时'),
                instance: gettext('任务分类'),
                prop: gettext('所属业务'),
                nodeName: gettext('各任务中实际执行的原子节点、子流程节点、网关节点个数'),
                detailsName: gettext('各任务执行耗时')
            },
            appType: 'app',
            time: [0, 0],
            category: '',
            biz_cc_id: '',
            nodeData: [],
            detailsData: [],
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
            nodeTotal: 0, // table数据总条数,
            nodePageIndex: 1, // 当前页码
            nodeLimit: 15, // 每页数量
            nodePagination: {
                // 分页操作
                limit: this.nodeLimit,
                pageIndex: this.nodePageIndex,
                pageArray: [15, 25]
            },
            nodeOptions: {
                stripe: true, // 是否为斑马纹 table
                loading: false, // 是否添加表格loading加载动画
                highlightCurrentRow: true, // 是否支持当前行高亮显示
                mutiSelect: false, // 是否支持列表项选中功能
                filter: false, // 是否支持数据过滤功能
                action: true, // 是否支持表格操作功能
                border: true // 是否支持外边框
            },
            nodeColumns: [
                {
                    prop: 'businessName', // 识别id
                    label: gettext('所属业务'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
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
                    width: 250
                },
                {
                    prop: 'creator', // 识别id
                    label: gettext('创建人'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'category', // 识别id
                    label: gettext('所属类型'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'atomTotal', // 识别id
                    label: gettext('原子个数'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'subprocessTotal', // 识别id
                    label: gettext('子流程个数'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                },
                {
                    prop: 'gatewaysTotal', // 识别id
                    label: gettext('网关个数'), // 表头显示名称
                    align: 'center' // 对其格式，可选（right，left，center）
                    // width: 600 // 宽度可选，默认自适应
                }
            ],
            nodeOperates: {
                // width: 200,
                // fixed: 'right',
                flex: '0 0 100%',
                isShow: true, // 是否显示操作按钮
                data: [
                    {
                        label: gettext('查看'), // 按钮显示文字
                        show: true, // 是否展示该按钮
                        plain: true, // 是否为朴素按钮
                        cls: 'bk-button bk-primary btn-size-mini',
                        method: (index, row) => {
                            // 回调方法
                            this.nodeHandleEdit(index, row)
                        }
                    }
                ]
            },
            detailsTotal: 0, // table数据总条数,
            detailsPageIndex: 1, // 当前页码
            detailsLimit: 15, // 每页数量
            detailsPagination: {
                // 分页操作
                limit: this.datailsLimit,
                pageIndex: this.datailsPageIndex,
                pageArray: [15, 25]
            },
            detailsOptions: {
                stripe: true, // 是否为斑马纹 table
                loading: false, // 是否添加表格loading加载动画
                highlightCurrentRow: true, // 是否支持当前行高亮显示
                mutiSelect: false, // 是否支持列表项选中功能
                filter: false, // 是否支持数据过滤功能
                action: true, // 是否支持表格操作功能
                border: true // 是否支持外边框
            },
            detailsColumns: [
                {
                    prop: 'businessName',
                    label: gettext('所属业务'),
                    align: 'center'
                    // width: 600,
                },
                {
                    prop: 'instanceName', // 识别id
                    label: gettext('任务名称'), // 表头显示名称
                    align: 'center', // 对其格式，可选（right，left，center）
                    width: 400 // 宽度可选，默认自适应
                },
                {
                    prop: 'category',
                    label: gettext('所属类型'),
                    align: 'center'
                    // width: 600,
                },
                {
                    prop: 'executeTime',
                    label: gettext('耗时（秒）'),
                    align: 'center'
                    // width: 600,
                },
                {
                    prop: 'creator',
                    label: gettext('创建人'),
                    align: 'center'
                    // width: 600,
                }
            ],
            detailsOperates: {
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
                            this.detailsHandleEdit(index, row)
                        }
                    }
                ]
            },
            instanceShow: true,
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
        this.plotlyDataByCategory()
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
        ...mapActions('task/', [
            'queryInstanceData'
        ]),
        ...mapActions([
            'getBizList',
            'getCategorys'
        ]),
        // 切换每页显示的数量
        nodeHandleSizeChange (limit) {
            this.nodePageIndex = 1
            this.nodeLimit = limit
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByNode()
        },
        // 切换页码
        nodeHandleIndexChange (pageIndex) {
            this.nodePageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByNode()
        },
        nodeHandleEdit (index, row) {
            window.open(this.site_url + 'taskflow/execute/' + row.businessId + '/?instance_id=' + row.instanceId)
        },
        // 切换每页显示的数量
        detailsHandleSizeChange (limit) {
            this.detailsPageIndex = 1
            this.detailsLimit = limit
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByDetails()
        },
        // 切换页码
        detailsHandleIndexChange (pageIndex) {
            this.detailsPageIndex = pageIndex
            // 根据 pageSize 和 limit 进行请求发送
            this.dataTableDataByDetails()
        },
        // 选中行
        handleSelectionChange (val) {
        },
        // 编辑
        detailsHandleEdit (index, row) {
            console.info(this.site_url)
            window.open(this.site_url + 'taskflow/execute/' + row.businessId + '/?instance_id=' + row.instanceId)
        },
        handleFilter (value, row, column) {
            return row.code === value
        },
        handelAction () {
        },
        changeTabPanel (name) {
            switch (name) {
                case 'instance' :
                    this.plotlyDataByCategory()
                    break
                case 'prop' :
                    this.plotlyDataByBizCCId()
                    break
                case 'node' :
                    this.dataTableDataByNode()
                    break
                case 'details' :
                    this.dataTableDataByDetails()
                    break
            }
        },
        async queryPlotlyData (data, id, title, seriesTitle) {
            const templateData = await this.queryInstanceData(data)
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
            else if (id === 'instanceBar' && total === 0) {
                this.instanceShow = false
                return
            }
            else if (id === 'instanceBar') {
                this.instanceShow = true
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
                group_by: 'category',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    biz_cc_id: this.biz_cc_id,
                    finish_time: this.time[1]
                })
            }
            this.queryPlotlyData(data, 'instanceBar', gettext('任务个数和占比'))
        },
        plotlyDataByBizCCId () {
            const data = {
                group_by: 'biz_cc_id',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    category: this.category
                })
            }
            this.queryPlotlyData(data, 'propBar', gettext('任务个数和占比'))
        },
        async queryDataTableData (data) {
            const templateData = await this.queryInstanceData(data)
            switch (data.group_by) {
                case 'instance_node':
                    this.nodeData = templateData.data.groups
                    this.nodeTotal = templateData.data.total
                    this.nodePagination.pageIndex = 1
                    this.nodePageIndex = 1
                    break
                case 'instance_details':
                    this.detailsData = templateData.data.groups
                    this.detailsTotal = templateData.data.total
                    this.detailsPageIndex = 1
                    break
            }
        },
        dataTableDataByNode () {
            const data = {
                group_by: 'instance_node',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    biz_cc_id: this.biz_cc_id,
                    category: this.category
                }),
                pageIndex: this.nodePageIndex,
                limit: this.nodeLimit
            }
            this.queryDataTableData(data)
        },
        dataTableDataByDetails () {
            const data = {
                group_by: 'instance_details',
                conditions: JSON.stringify({
                    create_time: this.time[0],
                    finish_time: this.time[1],
                    biz_cc_id: this.biz_cc_id,
                    category: this.category
                }),
                pageIndex: this.detailsPageIndex,
                limit: this.detailsLimit
            }
            this.queryDataTableData(data)
        }
    }
}
</script>
