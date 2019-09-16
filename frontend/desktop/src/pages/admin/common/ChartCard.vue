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
    <div class="content-wrap">
        <div
            v-for="(chart, i) in charts"
            :key="chart.title"
            :class="chartClassNames[i]"
            v-bkloading="{ isLoading: chart.isLoading, opacity: 1 }"
        >
            <div class="clearfix">
                <div class="content-title">{{chart.title}}</div>
                <div class="content-date">
                    <div
                        v-for="(select, j) in chart.selects"
                        :key="chart.title + 'select' + j"
                        class="content-date-business"
                    >
                        <bk-select
                            v-model="select.model"
                            class="bk-select-inline"
                            :placeholder="select.placeholder"
                            :popover-width="260"
                            :clearable="select.clearable"
                            :searchable="select.searchable"
                            @selected="select.onSelected"
                            @clear="select.onClear">
                            <bk-option
                                v-for="(option, k) in select.options"
                                :key="k"
                                :id="option[select.option.key]"
                                :name="option[select.option.name]">
                            </bk-option>
                        </bk-select>
                    </div>
                </div>
            </div>
            <data-statistics :dimension-list="chart.dimensionList" :total-value="chart.totalValue"></data-statistics>
        </div>
    </div>
</template>
<script>
    import DataStatistics from '../common/dataStatistics.vue'

    export default {
        name: 'ChartCard',
        components: {
            DataStatistics
        },
        props: ['charts'],
        computed: {
            singleChart () {
                return this.charts.length === 1
            },
            chartClassNames () {
                const first = 'content-dimesion'
                const second = 'content-wrap-right'
                const single = 'content-dimesion atom-statistics atom-content'
                if (this.singleChart) {
                    return [single]
                }
                return [first, second]
            }
        }
    }
</script>
<style lang="scss">
.content-box {
    .content-wrap {
        .content-dimesion.atom-statistics.atom-content {
            width: 100%;
            .chart-statistics-tool .tool-name {
                width: 250px;
            }
        }
    }
}
</style>
