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
        <div class="percentage">
            <div>{{maxPercent + '%'}}</div>
            <div>{{maxPercent - maxPercent / 4 + '%'}}</div>
            <div>{{maxPercent - maxPercent / 2 + '%'}}</div>
            <div>{{maxPercent / 4 + '%'}}</div>
            <div>{{leastPercent}}</div>
        </div>
        <div class="chart-statistics-warp">
            <NoData v-if="!totalValue"></NoData>
            <div class="chart-statistics-box" v-for="(dimension, index) in sortDimensionList" :key="index" v-else>
                <div
                    :title="getPercentage(dimension.value) + '%'"
                    :class="[dimension.value ? 'chart-statistics-pillar' : 'chart-statistics-normal']"
                    :style="{ height: `${dimension.value ? dealProcess(dimension.value, totalValue, maxPercent) : 0.3}%` }">
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
                leastPercent: '0%'
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
                for (let i = 0; i < this.sortDimensionList.length; i++) {
                    list.push(this.sortDimensionList[i].value)
                }
                this.maxPercent = Math.ceil(Math.max.apply(null, list) / this.totalValue * 10) * 10
            }
        },
        methods: {
            getPercentage (value) {
                return (value / this.totalValue * 100).toFixed(2)
            },
            dealProcess (value, totalValue, maxPercent) {
                let result = ((value / totalValue * 100) / maxPercent) * 100 * 0.85
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
    .chart-statistics-warp {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        overflow-x: auto;
        overflow-y: hidden;
        margin: 0px 20px 0px 54px;
        background: linear-gradient(to bottom, #ccc 0, #ccc 1px, transparent 1px);
        background-size: 10% 76px;
        .chart-statistics-box {
            display: flex;
            height: 365px;
            width: 56px;
            margin: auto;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            .chart-statistics-pillar {
                width: 12px;
                height: 85%;
                background: #3a84ff;
            }
            .chart-statistics-time {
                height: 60px;
                font-size: 12px;
                line-height: 60px;
                white-space: nowrap;
            }
            .chart-statistic {
                font-size: 12px;
            }
            .incline {
                transform: rotate(-40deg);
            }
        }
    }
</style>
