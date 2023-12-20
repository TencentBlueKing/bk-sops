<template>
    <div class="percentage" v-bkloading="{ isLoading: dataLoading, opacity: 1, zIndex: 100 }">
        <section class="percentage-title">
            <ul class="panel">
                <li
                    v-for="item in dataList"
                    :key="item.dimension_id"
                    :class="['panel-item', { 'active': item.dimension_id === dimensionId }]"
                    @click="dimensionId = item.dimension_id">
                    {{ item.dimension_name }}
                </li>
            </ul>
            <slot></slot>
        </section>
        <section class="chart-wrapper">
            <div class="canvas-content" v-if="hasAmountBizTotal">
                <canvas :class="`${canvasId}-canvas`" style="height: 240px; width: 240px"></canvas>
                <div class="center-circle">
                    <span class="total">{{ statsInfo.total }}</span>
                    <span class="desc">{{ statsInfo.name + $t('总数') }}</span>
                </div>
            </div>
            <NoData v-else></NoData>
            <div class="percent-table">
                <bk-table
                    :data="statsList"
                    :outer-border="false"
                    :header-border="false">
                    <bk-table-column
                        v-for="item in tableColumn"
                        :key="item.prop"
                        :min-width="item.width"
                        :label="item.label"
                        :align="item.align"
                        :resizable="false"
                        show-overflow-tooltip
                        :render-header="renderTableHeader"
                        :prop="item.prop">
                        <template slot-scope="{ row, $index }">
                            <div v-if="item.prop === 'name'" class="business-name">
                                <span
                                    v-if="$index !== statsList.length - 1"
                                    class="color-block"
                                    :style="{ background: row.color }">
                                </span>
                                <span>{{ row.name }}</span>
                            </div>
                            <span v-else>{{ row[item.prop] }}</span>
                        </template>
                    </bk-table-column>
                    <NoData slot="empty"></NoData>
                </bk-table>
            </div>
        </section>
    </div>
</template>

<script>
    import BKChart from '@blueking/bkcharts'
    import i18n from '@/config/i18n/index.js'
    import NoData from '@/components/common/base/NoData.vue'

    const TABLE_COLUMN = [
        {
            width: 150,
            align: 'left',
            label: i18n.t('名称'),
            prop: 'name'
        },
        {
            align: 'left',
            label: i18n.t('数量'),
            prop: 'amount'
        },
        {
            align: 'left',
            label: i18n.t('占比'),
            prop: 'percentage'
        }
    ]
    export default {
        components: {
            NoData
        },
        props: {
            dataLoading: {
                type: Boolean,
                default: true
            },
            isTemp: {
                type: Boolean,
                default: true
            },
            dataList: {
                type: Array,
                default: () => []
            }
        },
        data () {
            return {
                tableColumn: TABLE_COLUMN,
                chart: null,
                canvasId: '',
                dimensionId: '',
                statsInfo: {
                    name: '',
                    total: 0
                },
                statsList: [],
                statsObj: {},
                hasAmountBizTotal: 0 // 所有业务有数量的总和
            }
        },
        watch: {
            dataList (val) {
                if (val.length) {
                    const { dimension_id } = this.dataList[0]
                    this.statsObj = {}
                    if (this.dimensionId) {
                        this.initData()
                    } else {
                        this.dimensionId = dimension_id
                    }
                }
            },
            dimensionId (val) {
                if (val) {
                    this.initData()
                }
            }
        },
        beforeDestroy () {
            if (this.chart) {
                this.chart.destroy()
            }
        },
        methods: {
            initData () {
                // 表格数据
                if (this.dimensionId in this.statsObj) {
                    const { statsList, name, total } = this.statsObj[this.dimensionId]
                    this.statsList = statsList
                    this.statsInfo.total = total
                    this.tableColumn[0].label = name
                } else {
                    const { info, dimension_name: name, dimension_total: total } = this.dataList.find(item => item.dimension_id === this.dimensionId)
                    this.statsInfo = {
                        name: this.isTemp ? i18n.t('流程') : i18n.t('任务'),
                        total
                    }
                    this.tableColumn[0].label = name || i18n.t('名称')
                    const statsList = info.map((item, index) => {
                        item.color = this.randomColor(index)
                        item.amount = item.value
                        item.percentage = total ? (Math.round(item.value / total * 10000) / 100.00 + '%') : '0%'
                        return item
                    })
                    statsList.push({
                        name: i18n.t('总计'),
                        amount: total,
                        percentage: total ? '100%' : '0%'
                    })
                    this.statsList = statsList
                    this.statsObj[this.dimensionId] = {
                        statsList,
                        name,
                        total
                    }
                }
                // 环形图数据
                this.canvasId = this.dimensionId.replace(/\_/g, '-')
                const labels = []
                const bgcColor = []
                const data = []
                let counts = 0
                const circleDataList = this.statsList.slice(0, -1)
                circleDataList.forEach(item => {
                    labels.push(item.name)
                    bgcColor.push(item.color)
                    data.push(item.value)
                    counts = counts + (item.value ? 1 : 0)
                })
                this.hasAmountBizTotal = counts
                this.$nextTick(() => {
                    if (this.chart) {
                        this.updateChart(labels, bgcColor, data, counts)
                    } else {
                        this.initChart(labels, bgcColor, data, counts)
                    }
                })
            },
            initChart (labels, backgroundColor, data, counts) {
                const context = document.querySelector(`.${this.canvasId}-canvas`)
                if (!context) return
                this.chart = new BKChart(context, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [
                            {
                                backgroundColor,
                                borderColor: '#fff',
                                borderWidth: counts === 1 ? 0 : 1,
                                data,
                                hoverBackgroundColor: 'rgba(0, 0, 0, 0.1)'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: false
                        },
                        title: true,
                        cutoutPercentage: 70,
                        elements: {
                            arc: {}
                        }
                    }
                })
            },
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
            },
            updateChart (labels, backgroundColor, data, counts) {
                this.chart.data.labels = labels
                const datasets = this.chart.data.datasets[0]
                datasets.backgroundColor = backgroundColor
                datasets.borderWidth = counts === 1 ? 0 : 1
                datasets.data = data
                this.chart.update()
            },
            randomColor (seed = 0) {
                const totalColors = 1000 // 最大支持颜色种类数
                // 计算对应下标
                const idx = (seed + 1) % totalColors
                // 默认返回红色
                let ret = 0xFF0000
                // RGB的最大值
                const full = 0xFFFFFF
                // 总共需要支持多少种颜色，若传0则取255
                const total = totalColors || 0xFF
                // 将所有颜色平均分成x份
                const perVal = full / total
                if (idx >= 0 && idx <= total) {
                    ret = perVal * idx
                }
                ret = Math.round(ret)
                // 转成RGB 16进制字符串
                ret = ret.toString(16).padEnd(6, 'f')
                return '#' + ret
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .percentage {
        position: relative;
        padding: 15px 48px 0 15px;
        height: 360px;
        background: #ffffff;
        border: 1px solid #dcdee5;
        border-radius: 3px;
        box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        margin-bottom: 20px;
        .percentage-title {
            margin-bottom: 40px;
            .panel {
                display: flex;
                align-items: center;
                .panel-item {
                    color: #313238;
                    font-size: 14px;
                    cursor: pointer;
                    margin-right: 16px;
                    &.active {
                        color: #1768ef;
                        font-weight: 700;
                    }
                }
            }
        }
        .chart-wrapper {
            display: flex;
            align-items: center;
            .canvas-content {
                width: 30%;
                height: 30%;
                min-width: 160px;
                min-height: 160px;
                max-width: 240px;
                max-height: 240px;
                position: relative;
                flex-shrink: 0;
                margin-right: 3%;
                .center-circle {
                    width: 140px;
                    height: 140px;
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    border-radius: 50%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    color: #444444;
                    .total {
                        font-size: 40px;
                        font-weight: 700;
                        margin-bottom: 15px;
                    }
                    .desc {
                        font-size: 16px;
                    }
                }
            }
            /deep/.percent-table {
                flex: 1;
                min-width: 300px;
                .bk-table {
                    td {
                        height: 32px;
                        border-bottom: 1px dashed #dadfe8;
                    }
                    th {
                        background: #fff;
                        border-bottom: 1px solid #dadfe8;
                    }
                    .bk-table-row-last {
                        td {
                            border-bottom: none;
                        }
                        &:hover > td {
                            background: #fff;
                        }
                    }
                    &::before {
                        display: none;
                    }
                    .bk-table-body-wrapper {
                        height: 200px;
                        overflow-x: hidden;
                        overflow-y: auto;
                        @include scrollbar;
                    }
                }
                .business-name {
                    .color-block {
                        display: inline-block;
                        width: 12px;
                        height: 12px;
                        margin-right: 8px;
                        vertical-align: middle;
                    }
                }
            }
        }
    }
</style>
