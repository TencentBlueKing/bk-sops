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
    <div class="chart-box">
        <div class="percentage" v-if="totalValue">
            <div>{{maxPercent}}</div>
            <div>{{maxPercent - maxPercent / 4}}</div>
            <div>{{maxPercent - maxPercent / 2}}</div>
            <div>{{maxPercent / 4}}</div>
            <div>{{leastPercent}}</div>
        </div>
        <div :class="['chart-statistics-warp', { stripe: totalValue }]">
            <NoData v-if="!totalValue"></NoData>
            <div
                class="chart-statistics-box"
                v-for="(dimension, index) in sortDimensionList"
                :key="index"
                :style="{ width: properWidth + 'px' }"
                v-else>
                <div class="chart-statistics-number">{{dimension.value}}</div>
                <div
                    :title="getPercentage(dimension.value) + '%'"
                    :class="[dimension.value ? 'chart-statistics-pillar' : 'chart-statistics-normal']"
                    :style="{ height: `${dimension.value ? dealProcess(dimension.value, maxPercent) : 0.3}%` }">
                </div>
                <div :class="['chart-statistics-time', { incline: isIncline }]">
                    <p class="tool-time" :title="dimension.name || dimension.time">{{dimension.name || dimension.time}} </p>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
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
                sortDimensionList: [],
                maxPercent: '',
                leastPercent: '0',
                properWidth: ''
            }
        },
        computed: {
            isIncline () {
                return this.sortDimensionList.length > 22
            }
        },
        watch: {
            dimensionList (val) {
                this.sortDimensionList = tools.deepClone(this.dimensionList)
                this.sortDimensionList.sort((val1, val2) => val2.value - val1.value)
            },
            timeTypeList (val) {
                this.sortDimensionList = tools.deepClone(val)
            },
            sortDimensionList () {
                const list = []
                let maxNumber = []
                for (let i = 0; i < this.sortDimensionList.length; i++) {
                    list.push(this.sortDimensionList[i].value)
                }
                maxNumber = Math.max.apply(null, list)
                if (maxNumber <= 100) {
                    this.maxPercent = Math.ceil(maxNumber / 10) * 10
                } else if (maxNumber <= 1000) {
                    this.maxPercent = Math.ceil(maxNumber / 100) * 100
                } else {
                    this.maxPercent = Math.ceil(maxNumber / 1000) * 1000
                }
                this.projectWidth()
            }
        },
        methods: {
            projectWidth () {
                if (this.sortDimensionList.length <= 9) {
                    this.properWidth = 100
                } else if (this.sortDimensionList.length > 9 && this.sortDimensionList.length <= 33) {
                    this.properWidth = 25
                } else if (this.sortDimensionList.length > 33 && this.sortDimensionList.length <= 94) {
                    this.properWidth = 10
                } else if (this.sortDimensionList.length > 94 && this.sortDimensionList.length <= 365) {
                    this.properWidth = 3
                } else {
                    this.properWidth = 1
                }
            },
            getPercentage (value) {
                return (value / this.totalValue * 100).toFixed(2)
            },
            dealProcess (value, maxPercent) {
                let result = value / maxPercent * 100 * 0.85
                if (result > 0 && result < 0.06) {
                    result = 0.6
                }
                return result
            }
        }
    }
</script>
<style lang="scss">
    .chart-box {
        min-width: 1320px;
        height: 365px;
    }
    .percentage {
        position: absolute;
        top: 64px;
        display: flex;
        width: 54px;
        height: 320px;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
    }
    .stripe {
            background: linear-gradient(to bottom, #dcdee5 0, #dcdee5 1px, transparent 1px);
        }
    .chart-statistics-warp {
        display: flex;
        height: 365px;
        flex-direction: row;
        flex-wrap: nowrap;
        justify-content: space-around;
        overflow: hidden;
        margin: 0px 20px 0px 54px;
        padding: 0 20px;
        background-size: 10% 76px;
        .chart-statistics-normal {
            display: inline-block;
            width: 70%;
            height: 12px;
            background-color: #c0c4cc;
            vertical-align: baseline;
        }
        .chart-statistics-box {
            display: flex;
            height: 365px;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            .chart-statistics-pillar {
                width: 80%;
                height: 85%;
                background: #3a84ff;
            }
            .chart-statistics-time {
                height: 61px;
                font-size: 12px;
                line-height: 60px;
                white-space: nowrap;
            }
            .chart-statistic, .chart-statistics-number {
                font-size: 12px;
            }
            .incline {
                transform: rotate(-40deg);
            }
        }
    }
</style>
