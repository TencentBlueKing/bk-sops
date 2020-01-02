/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="chart-box">
        <NoData v-if="!totalValue"></NoData>
        <div id="chart-statistics-div" v-else></div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import Plotly from 'plotly.js/dist/plotly-basic.min.js'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'VerticalBarChart',
        components: {
            NoData
        },
        props: {
            dimensionList: {
                type: Array,
                default () {
                    return []
                }
            },
            totalValue: {
                type: Number,
                default () {
                    return 0
                }
            },
            timeTypeList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                chart: null,
                sortDimensionList: [],
                isUpdated: false,
                i18n: {
                    date: gettext('日期'),
                    task: gettext('任务')
                }
            }
        },
        watch: {
            dimensionList (val) {
                this.sortDimensionList = tools.deepClone(this.dimensionList)
                this.sortDimensionList.sort((val1, val2) => val2.value - val1.value)
            },
            timeTypeList (val) {
                this.sortDimensionList = tools.deepClone(val)
                if (this.isUpdated === true) {
                    this.initChart()
                }
            }
        },
        updated () {
            if (this.totalValue) {
                this.isUpdated = true
                this.initChart()
            }
        },
        methods: {
            initChart () {
                const x = []
                const y = []
                const text = []
                this.sortDimensionList.forEach(item => {
                    x.push(item.time)
                    y.push(item.value)
                    text.push(`${this.i18n.date}：${item.time}    ${this.i18n.task}：${item.value}`)
                })
                const max = Math.max(...y)
                const RangeMax = max < 100 ? Math.floor((max / 10 + 1)) * 10 : Math.floor((max / 100 + 1)) * 100
                const data = [{
                    x,
                    y,
                    text,
                    marker: {
                        color: '#3a84ff'
                    },
                    hoverinfo: 'text',
                    hoverlabel: {
                        bgcolor: '#000',
                        font: {
                            color: '#fff'
                        }
                    },
                    type: 'bar'
                }]
                const layout = {
                    height: 365,
                    font: {
                        size: 12,
                        color: '#63656e'
                    },
                    margin: {
                        t: 10,
                        b: 80
                    },
                    yaxis: {
                        fixedrange: true,
                        range: [0, RangeMax]
                    },
                    xaxis: {
                        fixedrange: true,
                        type: 'category',
                        tickmode: 'auto'
                    }
                }
                this.chart = Plotly.newPlot('chart-statistics-div', data, layout, { displayModeBar: false })
            }
        }
    }
</script>
<style lang="scss">
    .chart-box {
        min-width: 1320px;
        min-height: 365px;
        .no-data-wrapper {
            padding-top: 130px;
        }
    }
</style>
