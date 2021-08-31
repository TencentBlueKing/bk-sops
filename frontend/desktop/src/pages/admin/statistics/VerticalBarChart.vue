/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="vertical-bar-chart">
        <h3 class="chart-title">{{title}}</h3>
        <bk-form class="select-wrapper" form-type="inline">
            <bk-form-item
                v-for="selector in selectorList.slice(0, -1)"
                :key="selector.id">
                <bk-select
                    class="statistics-select"
                    :searchable="true"
                    :clearable="selector.clearable !== false"
                    :placeholder="selector.placeholder"
                    :disabled="selector.options.length === 0"
                    :value="selector.selected"
                    @change="onOptionClick(selector.id, $event)">
                    <bk-option
                        v-for="option in selector.options"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                        {{option.name}}
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item>
                <div class="bk-button-group">
                    <bk-button
                        v-for="option in timeOptions"
                        :key="option.id"
                        :class="{ 'is-selected': option.id === time }"
                        size="small"
                        @click="time = option.id">
                        {{ option.name }}
                    </bk-button>
                </div>
            </bk-form-item>
        </bk-form>
        <div class="chart-wrapper" ref="chartWrap" v-bkloading="{ isLoading: dataLoading, opacity: 1, zIndex: 100 }">
            <canvas v-if="dataList.length > 0" class="bar-chart-canvas" style="height: 100%;"></canvas>
            <no-data v-else></no-data>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import BKChart from '@blueking/bkcharts'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'VerticalBarChart',
        components: {
            NoData
        },
        props: {
            title: {
                type: String,
                default: ''
            },
            selectorList: {
                type: Array,
                default () {
                    return []
                }
            },
            dataList: {
                type: Array,
                default () {
                    return []
                }
            },
            dataLoading: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                time: 'day',
                timeOptions: [
                    {
                        id: 'day',
                        name: i18n.tc('天', 0)
                    },
                    {
                        id: 'month',
                        name: i18n.t('月')
                    }
                ],
                chartInstance: null
            }
        },
        watch: {
            dataList: {
                handler (val) {
                    if (val.length > 0) {
                        this.$nextTick(() => {
                            const x = []
                            const y = []
                            this.dataList.forEach(item => {
                                x.push(item.time)
                                y.push(item.value)
                            })
                            if (this.chartInstance) {
                                this.updateChart(x, y)
                            } else {
                                this.initChart(x, y)
                            }
                        })
                    }
                }
            }
        },
        methods: {
            initChart (x, y) {
                const ctx = this.$refs.chartWrap.querySelector('.bar-chart-canvas').getContext('2d')
                this.chartInstance = new BKChart(ctx, {
                    type: 'bar',
                    data: {
                        labels: x,
                        datasets: [{
                            data: y,
                            backgroundColor: '#3a84ff',
                            maxBarThickness: 24,
                            clip: '',
                            label: 'Rainfall1'
                        }, {
                            data: [10, 20, 30, 40, 50, 55, 33, 22, 11, 66, 55, 33, 66, 77, 22, 44, 22, 66, 32, 52],
                            backgroundColor: '#ff9c4a',
                            maxBarThickness: 24,
                            clip: '',
                            label: 'Rainfall11'
                        }, {
                            data: [55, 33, 66, 77, 22, 44, 22, 66, 32, 52, 12, 32, 12, 44, 25, 26, 14, 17, 35, 19],
                            backgroundColor: '#f8d30f',
                            maxBarThickness: 24,
                            clip: '',
                            label: 'Rainfall111'
                        }, {
                            data: [12, 32, 12, 44, 25, 26, 14, 17, 35, 19, 10, 20, 30, 40, 50, 55, 33, 22, 11, 66],
                            backgroundColor: '#3bce95',
                            maxBarThickness: 24,
                            clip: '',
                            label: 'Rainfall1111'
                        }]
                    },
                    options: {
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            crosshair: {
                                enabled: true
                            },
                            tooltip: {
                                // Disable the on-canvas tooltip
                                enabled: false,
                                custom: function (context) {
                                    // Tooltip Element
                                    let tooltipEl = document.getElementById('chartjs-tooltip')

                                    // Create element on first render
                                    if (!tooltipEl) {
                                        tooltipEl = document.createElement('div')
                                        tooltipEl.id = 'chartjs-tooltip'
                                        document.body.appendChild(tooltipEl)
                                    }

                                    // Hide if no tooltip
                                    const tooltipModel = context.tooltip
                                    if (tooltipModel.opacity === 0) {
                                        tooltipEl.style.opacity = 0
                                        return
                                    }

                                    // Set caret Position
                                    tooltipEl.classList.remove('above', 'below', 'no-transform')
                                    if (tooltipModel.yAlign) {
                                        tooltipEl.classList.add(tooltipModel.yAlign)
                                    } else {
                                        tooltipEl.classList.add('no-transform')
                                    }

                                    function getBody (bodyItem) {
                                        return bodyItem.lines
                                    }

                                    // 求百分率
                                    function getPercentage (num, total) {
                                        return (Math.round(num / total * 10000) / 100.00 + '%')
                                    }

                                    // Set Text
                                    if (tooltipModel.body) {
                                        const titleLines = tooltipModel.title || []
                                        const bodyLines = tooltipModel.body.map(getBody)

                                        let innerHtml = '<p class="tip-title">'

                                        titleLines.forEach(function (title) {
                                            innerHtml += title
                                        })
                                        innerHtml += '</p>'

                                        bodyLines.forEach(function (body, i) {
                                            const colors = tooltipModel.labelColors[i]
                                            let style = 'background:' + colors.backgroundColor
                                            style += '; border-color:' + colors.borderColor
                                            const taskName = body[0].split(': ') || []
                                            const taskNum = taskName[1] || body[0]
                                            innerHtml += '<div class="content-item">'
                                                + '<span class="color-block" style="' + style + '"></span>'
                                                + `<span class="task-name">${taskName[0]}</span>`
                                                + `<span class="task-num">${taskNum}</span>`
                                                + `<span class="percentage">(${getPercentage(taskNum, 100)})</span>`
                                                + '</div>'
                                        })

                                        tooltipEl.innerHTML = innerHtml
                                    }

                                    const position = context.chart.canvas.getBoundingClientRect()
                                    console.log(context, '33333333333')

                                    // position
                                    tooltipEl.style.left = position.left + tooltipModel.x + 'px'
                                    tooltipEl.style.top = position.top + tooltipModel.y + 'px'
                                    tooltipEl.style.opacity = 1
                                }
                            }
                        },
                        scales: {
                            x: {
                                stacked: true,
                                gridLines: {
                                    display: false
                                }
                            },
                            y: {
                                stacked: true,
                                gridLines: {
                                    borderDash: [5, 3]
                                }
                            }
                        }
                    }
                })
            },
            updateChart (x, y) {
                this.chartInstance.data.datasets[0].data = y
                this.chartInstance.data.labels = x
                this.chartInstance.update()
            },
            onOptionClick (selector, id) {
                this.$emit('onFilterClick', id, selector)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .vertical-bar-chart {
        position: relative;
        padding: 20px 20px 0;
        background: #ffffff;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        .chart-title {
            margin: 0;
            font-size: 14px;
        }
        .select-wrapper {
            position: absolute;
            top: 14px;
            right: 20px;
        }
        .chart-wrapper {
            margin-top: 20px;
            padding-bottom: 20px;
            height: 365px;
        }
        .no-data-wrapper {
            padding-top: 130px;
        }
        .bk-button-group {
            transform: translateY(-2px);
            .bk-button {
                min-width: 54px;
            }
        }
        
    }
</style>
<style lang="scss">
    #chartjs-tooltip {
        position: absolute;
        padding: 6px 12px;
        background: rgba(0, 0, 0, 0.8);
        border: none;
        border-radius: 6px;
        pointer-events: none;
        font-size: 12px;
        color: #fff;
        .tip-title {
            font: bold 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin-bottom: 5px;
            font-size: 14px;
        }
        .content-item {
            display: flex;
            align-items: center;
            margin-bottom: 3px;
            font: 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
            .color-block {
                height: 10px;
                width: 10px;
                margin-right: 4px;
                border-width: 2px;
            }
            .task-name {
                min-width: 80px;
            }
            .task-num {
                min-width: 25px;
                text-align: right;
            }
            .percentage {
                color: #979ba5;
                margin-left: 5px;
            }
        }
    }
</style>
