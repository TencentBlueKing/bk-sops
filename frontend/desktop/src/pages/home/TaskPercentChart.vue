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
    <div class="task-percent-chart-content">
        <h3 class="title">{{i18n.percent}}</h3>
        <div id="chart-wrap" v-if="totalTask"></div>
        <div v-else class="chart-empty">
            <NoData></NoData>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import Plotly from 'plotly.js/dist/plotly-basic.min.js'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'TaskPercentChart',
        components: {
            NoData
        },
        props: ['taskCount', 'totalTask'],
        data () {
            return {
                chart: null,
                i18n: {
                    percent: gettext('任务分类占比')
                }
            }
        },
        mounted () {
            if (this.totalTask) {
                this.initChart()
            }
        },
        methods: {
            initChart () {
                const colors = ['#7275ec', '#3c96ff', '#4bc6f3', '#f5c749', '#ed6b89', '#ff5256', '#85c030']
                const values = []
                const labels = []
                this.taskCount.forEach(item => {
                    values.push(item.value)
                    labels.push(item.name)
                })
                const data = [{
                    values,
                    labels,
                    marker: {
                        colors
                    },
                    hole: 0.6,
                    sort: false,
                    direction: 'clockwise',
                    type: 'pie'
                }]
                const layout = {
                    width: 500,
                    height: 340
                }
                this.chart = Plotly.newPlot('chart-wrap', data, layout, { displayModeBar: false })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-percent-chart-content {
    padding: 30px;
    .title {
        margin: 0;
        font-size: 16px;
    }
    .chart-empty {
        margin-top: 140px;
    }
}
</style>
