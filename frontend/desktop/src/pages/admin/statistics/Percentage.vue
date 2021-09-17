<template>
    <div class="percentage">
        <section class="percentage-title">
            <p class="title">{{ title }}</p>
            <slot></slot>
        </section>
        <section class="chart-wrapper">
            <div class="canvas-content">
                <canvas :class="`${canvasId}-canvas`" style="height: 100%; width: 100%"></canvas>
                <div class="center-circle">
                    <span class="total">368</span>
                    <span class="desc">BG总数</span>
                </div>
            </div>
            <div class="percent-table">
                <bk-table
                    :data="dataList"
                    :outer-border="false"
                    :header-border="false">
                    <bk-table-column
                        v-for="item in tableColumn"
                        :key="item.prop"
                        :min-width="item.width"
                        :label="item.label"
                        :align="item.align"
                        :resizable="false"
                        :prop="item.prop">
                        <template slot-scope="{ row, $index }">
                            <div v-if="item.prop === 'name'" class="business-name">
                                <span v-if="$index !== dataList.length - 1" class="color-block"></span>
                                <span>{{ row.name }}</span>
                            </div>
                            <span v-else>{{ row[item.prop] }}</span>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
        </section>
    </div>
</template>

<script>
    import BKChart from '@blueking/bkcharts'

    const TABLE_COLUMN = [
        {
            width: '200',
            align: 'left',
            label: '业务名称',
            prop: 'name'
        },
        {
            width: '',
            align: 'right',
            label: '数量',
            prop: 'source'
        },
        {
            width: '',
            align: 'right',
            label: '占比',
            prop: 'status'
        }
    ]
    export default {
        props: {
            title: {
                type: String,
                default: ''
            },
            canvasId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                tableColumn: TABLE_COLUMN,
                dataList: [
                    {
                        name: '王者荣耀手机版',
                        source: '61',
                        status: '12%'
                    }, {
                        name: '蓝鲸',
                        source: '61',
                        status: '12%'
                    }, {
                        name: '权限中心',
                        source: '61',
                        status: '12%'
                    }, {
                        name: '王者荣耀手机版',
                        source: '61',
                        status: '12%'
                    }, {
                        name: '蓝鲸',
                        source: '61',
                        status: '12%'
                    }, {
                        name: '权限中心',
                        source: '61',
                        status: '12%'
                    }, {
                        name: '总计',
                        source: '161',
                        status: '100%'
                    }
                ]
            }
        },
        mounted () {
            this.initChart()
        },
        methods: {
            initChart () {
                const context = document.querySelector(`.${this.canvasId}-canvas`)
                this.chart = new BKChart(context, {
                    type: 'doughnut',
                    data: {
                        labels: ['Running', 'Swimming', 'Eating', 'Cycling', 'Jumping', 'Sleeping'],
                        datasets: [
                            {
                                backgroundColor: [
                                    'rgba(51,157,255,1)',
                                    'rgba(59,206,149,1)',
                                    'rgba(255,156,74,1)',
                                    'rgba(255,111,114,1)',
                                    'rgba(248,211,15,1)',
                                    'rgba(181, 104, 255, 1)'
                                ],
                                borderColor: '#fff',
                                borderWidth: 1,
                                data: [20, 10, 30, 50, 40, 60],
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
        .percentage-title {
            margin-bottom: 40px;
            .title {
                color: #313238;
                font-size: 14px;
                font-weight: 700;
            }
        }
        .chart-wrapper {
            display: flex;
            .canvas-content {
                width: 240px;
                height: 240px;
                position: relative;
                flex-shrink: 0;
                margin-right: 40px;
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
                min-width: 352px;
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
                    display: flex;
                    align-items: center;
                    .color-block {
                        width: 12px;
                        height: 12px;
                        background: #ff6f72;
                        margin-right: 8px;
                    }
                }
            }
        }
    }
</style>
