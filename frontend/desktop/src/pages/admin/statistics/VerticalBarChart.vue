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
                v-for="selector in selectorList"
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
        </bk-form>
        <div class="chart-wrapper" ref="chartWrap" v-bkloading="{ isLoading: dataLoading, opacity: 1, zIndex: 100 }">
            <canvas v-if="dataList.length > 0" class="bar-chart-canvas" style="height: 100%;"></canvas>
            <no-data v-else></no-data>
        </div>
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
                            maxBarThickness: 24
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
                            }
                        },
                        scales: {
                            x: {
                                gridLines: {
                                    display: false
                                }
                            },
                            y: {
                                gridLines: {
                                    borderDash: [5, 3]
                                }
                            }
                        },
                        interaction: {
                            mode: 'nearest'
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
    }
</style>
