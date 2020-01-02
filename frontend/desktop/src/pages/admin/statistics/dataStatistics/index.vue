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
    <div class="chart-statistics-content">
        <NoData v-if="!totalValue"></NoData>
        <div class="chart-statistics-div" v-for="(dimension, index) in sortDimensionList" :key="index" v-else>
            <div class="chart-statistics-tool">
                <p class="tool-name" :title="dimension.name || dimension.time">{{dimension.name || dimension.time}} </p>
            </div>
            <div
                :class="[dimension.value ? 'chart-statistics-chart' : 'chart-statistics-normal']"
                :style="{ width: `${dimension.value ? dealProcess(dimension.value, totalValue) : 0.3}%` }">
            </div>
            <div class="chart-statistics-num">{{dimension.value}} / {{getPercentage(dimension.value)}}%</div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'DataStatistics',
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
                sortDimensionList: []
            }
        },
        watch: {
            dimensionList (val) {
                this.sortDimensionList = tools.deepClone(this.dimensionList)
                this.sortDimensionList.sort((val1, val2) => val2.value - val1.value)
            },
            timeTypeList (val) {
                this.sortDimensionList = tools.deepClone(val)
            }
        },
        methods: {
            getPercentage (value) {
                return (value / this.totalValue * 100).toFixed(2)
            },
            dealProcess (value, totalValue) {
                let result = value / totalValue * 60
                if (result > 0 && result < 0.06) {
                    result = 0.6
                }
                return result
            }
        }
    }
</script>

<style lang="scss">
.chart-statistics-content {
    height: 280px;
    overflow: auto;
    padding: 10px 22px 10px 22px;
    background: #ffff;
    .no-data-wrapper {
        height: 250px;
    }
}
.chart-statistics-dotted {
        margin: 5px;
        border-top: 1px dashed #dcdee5;
        height: 1px;
        overflow: hidden;
    }
    .chart-statistics-div {
        height: 34px;
        line-height:34px;
        border-top: 1px dashed #dcdee5;
        &:last-child {
            border-bottom: 1px dashed #dcdee5;
        }
    }
    .chart-statistics-tool {
        min-width:10%;
        padding-left: 20px;
        font-family: Microsoft YaHei;
        font-size: 14px;
        font-weight: normal;
        font-stretch: normal;
        color: #737987;
        display: inline-block;
        vertical-align: top;
        .tool-name {
            width: 100px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    }
    .chart-statistics-chart {
        display: inline-block;
        width: 70%;
        height: 12px;
        background-color: #3a84ff;
        vertical-align: baseline;
    }
    .chart-statistics-normal {
        display: inline-block;
        width: 70%;
        height: 12px;
        background-color: #c0c4cc;
        vertical-align: baseline;
    }
    .chart-statistics-num {
        margin-left: 15px;
        font-family: Arial;
        font-size: 12px;
        color: #63656e;
        display: inline-block;
        vertical-align: baseline;
    }
</style>
