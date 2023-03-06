/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
                    v-model="selector.selected"
                    @clear="onOptionClick(selector.id, '')"
                    @selected="onOptionClick(selector.id, $event)">
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
                        v-for="option in selectorList.slice(-1)[0].options"
                        :key="option.id"
                        :class="{ 'is-selected': option.id === selectorList.slice(-1)[0].selected }"
                        size="small"
                        @click="onOptionClick('type', option.id)">
                        {{ option.name }}
                    </bk-button>
                </div>
            </bk-form-item>
        </bk-form>
        <div v-if="dataLoading || dataList.length" class="chart-wrapper" ref="chartWrap" v-bkloading="{ isLoading: dataLoading, opacity: 1, zIndex: 100 }">
            <canvas class="bar-chart-canvas" style="height: 100%;"></canvas>
        </div>
        <NoData
            v-else
            :type="isSearch ? 'search-empty' : 'empty'"
            :message="isSearch ? $t('搜索结果为空') : ''"
            @searchClear="handleSearchClear">
        </NoData>
    </div>
</template>
<script>
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
            colorBlockList: {
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
                chartInstance: null
            }
        },
        computed: {
            isSearch () {
                return this.selectorList.slice(0, -1).some(item => item.selected)
            }
        },
        watch: {
            dataList: {
                handler (val) {
                    if (val.length > 0) {
                        this.$nextTick(() => {
                            const x = []
                            this.dataList.forEach(item => {
                                x.push(item.time)
                            })
                            const y = this.getDatasets()
                            if (this.chartInstance) {
                                this.updateChart(x, y)
                            } else {
                                this.initChart(x, y)
                            }
                        })
                    } else {
                        this.chartInstance = null
                    }
                }
            }
        },
        methods: {
            getDatasets () {
                const createMethodList = []
                this.dataList.forEach(item => {
                    this.colorBlockList.forEach(val => {
                        const isHas = item.create_method.some(method => method.name === val.value)
                        if (!isHas) {
                            item.create_method.push({
                                name: val.value,
                                value: 0
                            })
                        }
                    })
                    createMethodList.push(...item.create_method)
                })
                const createMethodObj = createMethodList.reduce((acc, cur) => {
                    acc[cur.name] ? acc[cur.name].push(cur.value) : (acc[cur.name] = [cur.value])
                    return acc
                }, {})
                const datasets = []
                for (const [key, value] of Object.entries(createMethodObj)) {
                    const colorBlock = this.colorBlockList.find(item => item.value === key)
                    datasets.push({
                        data: value,
                        backgroundColor: colorBlock ? colorBlock.color : '#3a84ff',
                        maxBarThickness: 24,
                        clip: '',
                        label: colorBlock.text
                    })
                }
                return datasets
            },
            initChart (x, y) {
                const ctx = this.$refs.chartWrap.querySelector('.bar-chart-canvas').getContext('2d')
                this.chartInstance = new BKChart(ctx, {
                    type: 'bar',
                    data: {
                        labels: x,
                        datasets: y
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
                                        return (Math.round(Number(num) / total * 10000) / 100.00 + '%')
                                    }

                                    // 计算left, top
                                    function getToolTipElLeftOrTop (tooltipModel) {
                                        const { x: xAxes, y: yAxes } = tooltipModel
                                        const xSubscript = tooltipModel.title[0] // 当前hover的x轴坐标内容
                                        const { left: chartLeft, top: chartTop } = context.chart.canvas.getBoundingClientRect()
                                        // 获取默认内容格式的最大宽度
                                        const hideDomList = Array.from(tooltipEl.querySelectorAll('.hide-task-name'))
                                        const hideDomWdithList = hideDomList && hideDomList.map(dom => {
                                            return dom.getBoundingClientRect().width
                                        })
                                        const hideDomMaxWdith = Math.max(...hideDomWdithList)
                                        // 获取自定义内容的宽度
                                        const contentDom = tooltipEl.querySelector('.task-method-item')
                                        const { width: contentWidth } = contentDom && contentDom.getBoundingClientRect()
                                        const median = Math.ceil(x.length / 2) // x轴坐标中间值
                                        const index = x.findIndex(item => item === xSubscript) // 当前x轴坐标
                                        // 当前x轴坐标大于中间值时重新计算left
                                        const left = chartLeft + xAxes - (index + 1 > median ? (contentWidth - 2 - hideDomMaxWdith) : 0)
                                        const top = chartTop + yAxes
                                        return { left, top }
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

                                        const total = bodyLines.reduce((acc, cur) => {
                                            const textArr = cur[0].split(': ') || []
                                            const num = textArr[1].replace(/,/g, '')
                                            acc = Number(acc) + Number(num)
                                            return acc
                                        }, [])
                                        bodyLines.forEach(function (body, i) {
                                            const colors = tooltipModel.labelColors[i]
                                            let style = 'background:' + colors.backgroundColor
                                            style += '; border-color:' + colors.borderColor
                                            const textArr = body[0].split(': ') || []
                                            const taskNum = textArr[1].replace(/,/g, '')
                                            if (taskNum !== '0') {
                                                innerHtml += '<div class="task-method-item">'
                                                    + '<span class="color-block" style="' + style + '"></span>'
                                                    + `<span class="task-name">${textArr[0]}</span>`
                                                    + `<span class="hide-task-name">${body[0]}</span>`
                                                    + `<span class="task-num">${taskNum}</span>`
                                                    + `<span class="percentage">(${getPercentage(taskNum, total)})</span>`
                                                    + '</div>'
                                            }
                                        })

                                        tooltipEl.innerHTML = innerHtml
                                    }
                                    const { left, top } = getToolTipElLeftOrTop(tooltipModel)

                                    // position
                                    tooltipEl.style.left = left + 'px'
                                    tooltipEl.style.top = top + 'px'
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
                this.chartInstance.data.datasets = y
                this.chartInstance.data.labels = x
                this.chartInstance.update()
            },
            onOptionClick (selector, id) {
                this.$emit('onFilterClick', id, selector)
            },
            handleSearchClear () {
                this.$emit('onClearTimeFilter')
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
        margin-bottom: 20px;
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
        .bk-button-group {
            transform: translateY(-2px);
            .bk-button {
                min-width: 54px;
            }
        }

    }
</style>
